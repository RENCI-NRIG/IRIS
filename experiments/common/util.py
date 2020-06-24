#!/usr/bin/env python
import os
import subprocess
import datetime
import time

def wget(url: str, http_proxy: str = None) -> None:
    cmd = ""
    if http_proxy:
        cmd.append("http_proxy={} ".format(http_proxy))
    
    cmd.append("wget {}".format(url))

    wget_proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(wget_proc.stdout.decode())
    if wget_proc.returncode != 0:
        print("failed command: {}".format(cmd))
        print(wget_proc.stderr.decode())
        sys.exit(1)
   
def pegasus_config_python() -> str:
    pegasus_config = subprocess.run(["pegasus-config", "--python"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if pegasus_config.returncode != 0:
        raise RuntimeError(pegasus_config.stderr)

    return pegasus_config.stdout.decode().strip()

def restart_caches(*hostnames) -> None:
    for host in hostnames:
        print("starting restart of iris-http-proxy on host: {}".format(host))
        p = subprocess.run(["ssh", host, "sudo", "systemctl", "restart", "iris-http-proxy"])
        assert p.returncode == 0
        print("restart of iris-http-proxy on host: {} complete".format(host))

def clear_caches(*hostnames) -> None:
    for host in hostnames:
        print("starting cache cleanup at: {}".format(host))
        p = subprocess.run(["ssh", host, "sudo", "rm", "-f", "/cache/*"])
        assert p.returncode == 0
        print("cache cleanup complete")

def wait_on_pegasus_dagman() -> None:
    while True:
        p = subprocess.run(
                ["ps", "-eo", "command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        if "pegasus-dagman" in p.stdout.decode():
            print("pegasus-dagman still up {}".format(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            time.sleep(1)
        else:
            break
    print("pegasus-dagman down")
