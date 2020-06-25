# A simple HTTP proxy which does caching of requests.
# "Inspired" by: https://gist.github.com/justinmeiners/24dcf5904490b621220bed643651f681
# but updated with
# - a clean exit on signal allowing it to be easily popped by another script using subprocess
# - tcp socket reuse to avoid the tcp socket already in use if popped often
# - a cache directory to avoid a lot of files just being in the middle
#
# duplicate the class+tcpserver and listen on another port for your https needs;
# it will share the cache

import http.server
import socketserver
import urllib.request
import shutil
import os
import hashlib
import signal
import time

from pathlib import Path
from urllib.parse import urlparse

cache_base = "./cache/"
httpd = None

def print_green(a, **kwargs): print("\033[92m{}\033[00m".format(a), **kwargs)
def print_yellow(a, **kwargs): print("\033[93m{}\033[00m".format(a), **kwargs)

def exit_gracefully(sig, stack):
    print("received sig %d, quitting" % (sig))
    httpd.server_close()
    exit()


class CacheHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        get_start = time.time()
        # m = hashlib.md5()
        # m.update(self.path.encode("utf-8"))
        # cache_filename = cache_base + m.hexdigest() +".cached"

        url = urlparse(self.path)

        # Option 1: file names aren't unique
        cache_filename = (
            cache_base
            + url.netloc.replace(":", "-")
            + url.path.replace("/", "-")
            + ".cached"
        )

        """
        # Option 2: file names are unique
        cache_filename = cache_base + Path(url.path).name + ".cached"
        """

        print("-" * 60)
        if not os.path.exists(cache_filename):
            print_yellow("cache miss: " + self.path)

            with open(cache_filename + ".temp", "wb") as output:
                req = urllib.request.Request(self.path)

                for k, v in self.headers.items():
                    # for each header that is not "Host"
                    # add that header to the request
                    if k not in ["Host"]:
                        req.add_header(k, self.headers[k])

                print("[START] req: {}".format(self.path))
                req_start = time.time()
                resp = urllib.request.urlopen(req)
                print("[COMPLETE] req: {0} | {1:.4f}s".format(self.path, time.time() - req_start))
                print("[START] write: {}".format(output.name))
                write_start = time.time()
                shutil.copyfileobj(resp, output)
                print("[COMPLETE] write: {0} | {1:.4f}s".format(output.name, time.time() - write_start))
                os.rename(cache_filename + ".temp", cache_filename)
        else:
            print_green("cache hit: " + self.path)

        print("[START] copy to self.wfile: {}".format(cache_filename))
        copy_start = time.time()
        with open(cache_filename, "rb") as cached:
            self.send_response(200)
            self.end_headers()
            shutil.copyfileobj(cached, self.wfile)
        print("[COMPLETE] copy: {0} | {1:.4f}s".format(cache_filename, time.time() - copy_start))
        print("resp time: {0:.4f}".format(time.time() - get_start))


signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", 8000), CacheHandler)
if not os.path.exists(cache_base):
    os.mkdir(cache_base)

httpd.serve_forever()
