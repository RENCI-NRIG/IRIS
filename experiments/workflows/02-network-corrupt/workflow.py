#!/usr/bin/env python3
import argparse
import getpass
import hashlib
import os
import subprocess
import sys
import logging as log

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

log.basicConfig(level=log.DEBUG)

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
                description="Run a workflow with N independent jobs."
            )

    parser.add_argument(
                "dir",
                help="Test directory for this workflow. One will be created if"
                " it already does not exist."
            )

    parser.add_argument(
                "run_id",
                help="Run dir that will be created for this workflow in <dir>."
            )

    parser.add_argument(
                "num_jobs",
                type=int,
                choices=range(1, 1001),
                metavar="[1, 1000]",
                help="The number of independent workflow jobs to run."
            )
    
    parser.add_argument(
                "-t",
                "--timestamps-file",
                help="Path to write timestamp file to."
            )

    return parser.parse_args()

def sha256(fname):
    with open(fname,"rb") as f:
        _bytes = f.read()
        return hashlib.sha256(_bytes).hexdigest()

### Workflow Setup #############################################################
if __name__=="__main__":
    args = parse_args()
    
    BASE_DIR = Path(__file__).parent.resolve()

    # create DIR (1 or more test runs)
    WORK_DIR = Path(args.dir)
    try:
        Path.mkdir(WORK_DIR)
    except FileExistsError:
        # other runs might want to run in this directory
        pass

    assert WORK_DIR.is_dir()
    log.info("test directory set to: {}".format(WORK_DIR))

    # --- Properties ------------------------------------------------------------
    props = Properties()
    props["pegasus.data.configuration"] = "nonsharedfs"
    props["pegasus.transfer.bypass.input.staging"] = "True"
    props["pegasus.monitord.encoding"] = "json"
    props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
    props["dagman.retry"] = "2"
    props["pegasus.transfer.arguments"] = "-m 1"
    props.write(str(BASE_DIR / "pegasus.properties"))
    
    # --- Sites ----------------------------------------------------------------
    sites.write_basic_site_catalog(
        str(BASE_DIR / "sites.yml"), 
        str(WORK_DIR), 
        args.run_id
    )

    # --- Transformations - Replicas - Workflow ---------------------------------
    username = getpass.getuser()
    base_dir = os.getcwd()

    wf = Workflow("01-bypass")

    # transformations
    tc = TransformationCatalog()
    script = Transformation(
                            'job.sh',
                            site='uc-staging',
                            pfn='http://uc-staging.data-plane/~{}/inputs/job-wrapper.sh'.format(username),
                            is_stageable=True,
                            checksum={"sha256":sha256("job-wrapper.sh")}
                        )
    tc.add_transformations(script)

    # a list of common inputs for all jobs
    inputs = []
    urls = []
    rc = ReplicaCatalog()
    for entry in os.listdir('inputs/'):
        infile = File(entry)
        inputs.append(infile)
        chksum = sha256('inputs/{}'.format(entry))
        pfn = 'http://uc-staging.data-plane/~{}/inputs/{}'.format(username, entry)
        urls.append(pfn)
        rc.add_replica(
                    'uc-staging',
                    infile,
                    pfn,
                    checksum={"sha256": chksum}
                )

    for i in range(args.num_jobs):
        j = Job(script).add_args(i).add_inputs(*inputs)
        wf.add_jobs(j)

    wf.add_transformation_catalog(tc)
    wf.add_replica_catalog(rc)

    if args.timestamps_file:
        with open(args.timestamps_file, "w") as f:
            f.write(datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " START")

    # start workflow
    try:
        log.info("planning and submitting workflow with {} jobs".format(args.num_jobs))
        wf.plan(
                output_site="local",
                dir=str(WORK_DIR),
                relative_dir=args.run_id,
                sites=["condorpool"],
                staging_sites={"condorpool": "origin"},
                submit=True
        )\
        .wait()

    except PegasusClientError as e:
        log.error(e.output)
    finally:
        if args.timestamps_file:
            with open(args.timestamps_file, 'a') as f:
                f.write('\n' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " END")

        # ensure pegasus-dagman is down
        util.wait_on_pegasus_dagman()







