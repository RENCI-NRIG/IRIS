#!/usr/bin/env python
import os
import logging
import sys

from datetime import datetime
from pathlib import Path

################################################################################
######### Add if using anything defined in IRIS/experiments/common #############
sys.path.insert(0, str(Path(__file__).parent.parent.resolve() / "common"))

import util
import props
import sites
################################################################################

from Pegasus.api import *

logging.basicConfig(level=logging.DEBUG)

# --- Cleanup Caches -----------------------------------------------------------
util.clear_caches("syr-compute-c2", "unl-compute-c1", "ucsd-compute-c3")

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
            .add_inputs(*wc_job.get_inputs())\
            .add_outputs(final_of)

wf = Workflow(str(BASE_DIR), infer_dependencies=True)\
        .add_jobs(wc_job, tar_job)\
        .add_replica_catalog(rc)\
        .add_transformation_catalog(tc)\
        .plan(
                verbose=3,
                output_site="local", 
                dir=WORK_DIR, 
                relative_dir=RUN_ID, 
                sites=["condorpool"], 
                staging_sites={"condorpool": "origin"}
        )\
        .wait()