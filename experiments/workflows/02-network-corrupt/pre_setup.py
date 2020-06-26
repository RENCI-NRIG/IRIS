#!/usr/bin/env python3
import logging as log
import sys
import os
import subprocess

from pathlib import Path

################################################################################
######### using IRIS/experiments/common and pegasus-config setup ###############
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))

import util
import props
import sites

sys.path.append(util.pegasus_config_python())
################################################################################

log.basicConfig(level=log.DEBUG)

BASE_DIR = Path(__file__).parent.resolve()
os.chdir(BASE_DIR)

# --- Cleanup Caches -------------------------------------------------------
util.restart_caches("syr-compute-c2", "unl-compute-c1", "ucsd-compute-c3")
util.clear_caches("syr-compute-c2", "unl-compute-c1", "ucsd-compute-c3")
log.info("caches cleared and restarted")

# --- Bypass Data Staging --------------------------------------------------
stage_cmd = ["ssh", "uc-staging.data-plane", "mkdir", "-p", "~/public_html/inputs"]
stage = subprocess.run(stage_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)   
if stage.returncode != 0:
    log.critical("Could not execute: {},\n{}\n{}".format(
            " ".join(stage_cmd),
            stage.stdout.decode(),
            stage.stderr.decode()
        ))
    sys.exit(1)

scp_cmd = " ".join(
    [
        "scp", str(BASE_DIR / "job-wrapper.sh"), str(BASE_DIR / "inputs/*"), 
        "uc-staging.data-plane:~/public_html/inputs/"
    ]
)
scp = subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
if scp.returncode != 0:
    log.critical("Could not execute: {},\n{}\n{}".format(
            scp_cmd,
            scp.stdout.decode(),
            scp.stderr.decode()
        ))
    sys.exit(1)
log.info("bypass staging complete")
