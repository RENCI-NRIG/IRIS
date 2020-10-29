#!/usr/bin/env python
import os
import subprocess
import datetime
import time
import sys
import logging

from pathlib import Path

def wget(url: str, http_proxy: str = None) -> None:

    cmd = ""
    if http_proxy:
        cmd += "http_proxy={} ".format(http_proxy)
    
    cmd += "wget {}".format(url)

    wget_proc = subprocess.run(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd="/tmp"
        )

    print(wget_proc.stdout.decode())
    print(wget_proc.stderr.decode())

    if wget_proc.returncode != 0:
        print("failed command: {}".format(cmd))
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

def wait_on_monitord(submit_dir: Path) -> None:
    # If monitord fails and is restarted, this won't work. However, we've agreed
    # that this solution is good enough for now. If there was a pid file for
    # pegasus-dagman, it would be preferred to wait on that instead.


    # if monitord.pid doesn't exist, we are done, else wait until monitor.d completes
    try:
        monitord_pid_file = submit_dir / "monitord.pid"
        # get pid from <submit_dir>/monitord.pid
        with monitord_pid_file.open() as f:
            mpid = int(f.read().split()[1].strip())

        # wait at most 10 min for monitord to finish, else something has gone probably wrong
        TIMEOUT = 600
        elapsed = 0
        while elapsed < TIMEOUT:
            try:
                # if this is successful monitord is still running
                os.kill(mpid, 0)
            except OSError as e:
                # ESRCH 3 No Such Process
                if e.errno != 3:
                    raise e
                else:
                    break

            print("{} monitord (pid={}) still running".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), mpid))
            time.sleep(1)
            elapsed += 1
        if elapsed >= TIMEOUT:
            print("wait_on_monitord timed out")
        else:
            print("monitord finished")

    except FileNotFoundError:
        print("{} not found. monitord is assumed to be done".format(monitord_pid_file))


def bypass_staging(wf_experiment_dir: Path, submit_site: str):
    experiment_dir = wf_experiment_dir.resolve()
    staging_site = "{}-staging.data-plane".format(submit_site)
    #staging_site = "{}-staging".format(submit_site)
    stage_cmd = ["ssh", staging_site, "mkdir", "-p", "~/public_html/inputs"]
    
    stage = subprocess.run(stage_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   

    if stage.returncode != 0:
        logging.critical("Could not execute: {},\n{}\n{}".format(
                " ".join(stage_cmd),
                stage.stdout.decode(),
                stage.stderr.decode()
            ))
        sys.exit(1)

    scp_cmd = " ".join(
        [
            "scp", str(experiment_dir / "job-wrapper.sh"), str(experiment_dir / "inputs/*"), 
            "{}:~/public_html/inputs/".format(staging_site)
        ]
    )
    scp = subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if scp.returncode != 0:
        logging.critical("Could not execute: {},\n{}\n{}".format(
                scp_cmd,
                scp.stdout.decode(),
                scp.stderr.decode()
            ))
        sys.exit(1)
    logging.info("bypass staging complete for site: {}".format(staging_site))
