#!/usr/bin/env python
import os
import subprocess

def pegasus_config_python() -> str:
    pegasus_config = subprocess.run(["pegasus-config", "--python"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if pegasus_config.returncode != 0:
        raise RuntimeError(pegasus_config.stderr)

    return str(pegasus_config.stdout).strip()

def clear_caches(*hostnames) -> None:
    for host in hostnames:
        print("starting cache cleanup at: {} for user: {}...".format(host, os.getenv("USER")))
        subprocess.run(["ssh", host, "sudo", "rm", "-f", "/cache/uc-staging-~$USER*"])
        print("cache cleanup complete")