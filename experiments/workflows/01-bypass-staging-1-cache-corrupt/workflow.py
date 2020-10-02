#!/usr/bin/env python3

import logging
import getpass
import hashlib
import os
import subprocess
import sys

from datetime import datetime
from pathlib import Path

################################################################################
######### using IRIS/experiments/common and pegasus-config setup ###############
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))

import util
import props
import sites

sys.path.append(util.pegasus_config_python())
################################################################################

from Pegasus.api import *

log = logging.getLogger("01-bypass-workflow")
log.setLevel(logging.DEBUG)

def sha256(fname):
    with open(fname,"rb") as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

# --- Work Directory Setup -----------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()

corrupt_site = None
if len(sys.argv) > 2:
    corrupt_site = sys.argv[1]
    run_id = sys.argv[2]

RUN_ID=BASE_DIR.name # cwd name
WORK_DIR = os.getenv("EXPERIMENT_WORK_DIR")
initiated_by_run_script = WORK_DIR

if not initiated_by_run_script:
    WORK_DIR = Path(os.getenv("HOME")) / "workflow-runs"
    RUN_ID += "-" + datetime.now().strftime("%s")

    try:
        Path.mkdir(WORK_DIR)
    except FileExistsError:
        pass

    WORK_DIR = str(WORK_DIR)

# --- Cleanup Caches -----------------------------------------------------------
util.restart_caches("syr-staging", "unl-staging", "ucsd-staging", "uc-staging")
util.clear_caches("syr-staging", "unl-staging", "ucsd-staging", "uc-staging")

# --- Place Data at Staging Site -----------------------------------------------
stage_cmd = ["ssh", "uc-staging.data-plane", "mkdir", "-p", "~/public_html/inputs"]
stage = subprocess.run(stage_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if stage.returncode != 0:
    log.critical("Could not execute: {},\n{}\n{}".format(
            " ".join(stage_cmd),
            stage.stdout.decode(),
            stage.stderr.decode()
        ))
    sys.exit(1)

scp_cmd = " ".join(["scp", str(BASE_DIR / "job-wrapper.sh"), str(BASE_DIR / "inputs/*"), "uc-staging.data-plane:~/public_html/inputs/"])
scp = subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
if scp.returncode != 0:
    log.critical("Could not execute: {},\n{}\n{}".format(
            scp_cmd,
            scp.stdout.decode(),
            scp.stderr.decode()
        ))
    sys.exit(1)

# --- Properties ---------------------------------------------------------------
props = Properties()
props["pegasus.data.configuration"] = "nonsharedfs"
props["pegasus.transfer.bypass.input.staging"] = "True"
props["pegasus.monitord.encoding"] = "json"
props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
props["dagman.retry"] = "2"
props["pegasus.transfer.arguments"] = "-m 1"
props.write(str(BASE_DIR / "pegasus.properties"))

# --- Sites --------------------------------------------------------------------
sites.write_basic_site_catalog(str(BASE_DIR / "sites.yml"), WORK_DIR, RUN_ID)

# --- Transformations - Replicas - Workflow ------------------------------------
# used all over the place
username = getpass.getuser()
base_dir = os.getcwd()

wf = Workflow(BASE_DIR.name)

# transformations
tc = TransformationCatalog()
script = Transformation('job.sh',
                        site='uc-staging',
                        pfn='http://uc-staging.data-plane/~{}/inputs/job-wrapper.sh'.format(username),
                        is_stageable=True)
tc.add_transformations(script)

# a list of common inputs for all jobs
inputs = []
rc = ReplicaCatalog()
for entry in os.listdir('inputs/'):
    infile = File(entry)
    inputs.append(infile)
    chksum = sha256('inputs/{}'.format(entry))
    rc.add_replica('uc-staging',
                   infile,
                   'http://uc-staging.data-plane/~{}/inputs/{}'.format(username, entry),
                    checksum_type='sha256',
                    checksum_value=chksum)

for i in range(100):
    j = Job(script)
    j.add_args(i)
    j.add_inputs(*inputs)
    wf.add_jobs(j)

wf.add_transformation_catalog(tc)
wf.add_replica_catalog(rc)

# start driver experiment
if corrupt_site:
    iris_experiment_driver = subprocess.Popen([str(BASE_DIR / "iris-experiment-driver"), corrupt_site, WORK_DIR, run_id])

# start workflow
try:
    wf.plan(
            output_site="local",
            dir=WORK_DIR,
            relative_dir=RUN_ID,
            sites=["condorpool"],
            staging_sites={"condorpool": "origin"},
            submit=True
    )\
    .wait()

except PegasusClientError as e:
    print(e.output)

# terminate driver
if corrupt_site:
    iris_experiment_driver.terminate()


# ensure pegasus-dagman is down
util.wait_on_pegasus_dagman()
