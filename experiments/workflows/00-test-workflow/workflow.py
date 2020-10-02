#!/usr/bin/env python3
import os
import sys
import subprocess

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

# --- Cleanup Caches -----------------------------------------------------------
util.restart_caches("syr-staging", "unl-staging", "ucsd-staging", "uc-staging")
util.clear_caches("syr-staging", "unl-staging", "ucsd-staging", "uc-staging")

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

# --- Properties ---------------------------------------------------------------
props.write_basic_properties(str(BASE_DIR / "pegasus.properties"))

# --- Sites --------------------------------------------------------------------
sites.write_basic_site_catalog(str(BASE_DIR / "sites.yml"), WORK_DIR, RUN_ID)

# --- Replicas -----------------------------------------------------------------
if_1 = File("input_1.txt")
if_2 = File("input_2.txt")
if_3 = File("input_3.txt")
if_4 = File("input_4.txt")

rc = ReplicaCatalog()\
        .add_replica("local", if_1, str(BASE_DIR / "inputs/input_1.txt"))\
        .add_replica("local", if_2, str(BASE_DIR / "inputs/input_2.txt"))\
        .add_replica("local", if_3, str(BASE_DIR / "inputs/input_3.txt"))\
        .add_replica("local", if_4, str(BASE_DIR / "inputs/input_4.txt"))

# --- Transformations ----------------------------------------------------------
wc = Transformation("wc", site="local", pfn=str(BASE_DIR / "wc.sh"), is_stageable=True)
tar = Transformation("tar", site="condorpool", pfn="/bin/tar", is_stageable=False)

tc = TransformationCatalog()\
        .add_transformations(wc, tar)

# --- Workflow -----------------------------------------------------------------
of = File("output.txt")
wc_job = Job(wc)\
            .add_args(if_1, if_2, if_3, if_4, of)\
            .add_inputs(if_1, if_2, if_3, if_4)\
            .add_outputs(of)

final_of = File("final_output.tar.gz")
tar_job = Job(tar)\
            .add_args("cvzf", final_of, if_1, if_2, if_3, if_4, of)\
            .add_inputs(*wc_job.get_inputs(), *wc_job.get_outputs())\
            .add_outputs(final_of)

wf = Workflow(BASE_DIR.name, infer_dependencies=True)\
        .add_jobs(wc_job, tar_job)\
        .add_replica_catalog(rc)\
        .add_transformation_catalog(tc)

# start driver experiment
iris_experiment_driver = subprocess.Popen([str(BASE_DIR / "iris-experiment-driver")])

# start workflow
try:
    wf.plan(
            force=True,
            output_sites=["local"], 
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
iris_experiment_driver.terminate()

# ensure pegasus-dagman is down
util.wait_on_pegasus_dagman()

