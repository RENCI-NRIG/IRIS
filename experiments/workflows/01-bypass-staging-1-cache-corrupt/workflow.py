#!/usr/bin/env python3

import getpass
import hashlib
import logging
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

logging.basicConfig(level=logging.DEBUG)

def sha256(fname):
    with open(fname,"rb") as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

# --- Work Directory Setup -----------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()

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
util.clear_caches("syr-compute-c2", "unl-compute-c1", "ucsd-compute-c3")

# --- Place Data at Staging Site -----------------------------------------------
stage = subprocess.run(["ssh", "uc-staging", "mkdir", "-p", "~/public_html/inputs"])

if stage.returncode != 0:
    raise RuntimeError()

scp = subprocess.run(" ".join(["scp", str(BASE_DIR / "job-wrapper.sh"), str(BASE_DIR / "inputs/*"), "uc-staging:~/public_html/inputs/"]), shell=True)
if scp.returncode != 0:
    raise RuntimeError()

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
                        pfn='http://uc-staging.date-plane/~{}/inputs/job-wrapper.sh'.format(username),
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
iris_experiment_driver = subprocess.Popen([str(BASE_DIR / "iris-experiment-driver")])

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

except Exception as e:
    print(e)
    # print(e.args[1].stderr)

# terminate driver 
iris_experiment_driver.terminate()
