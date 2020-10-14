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
                description="Run a workflow with N independent jobs. Multiple "
                " compute hosts may be corrupted if specified."
                " Example: 'workflow.py unl /home/ryan/test1 run1 30 -c syr-compute-c2 -c unl-compute-c1 -t /tmp/iris_timestamps/this_run.txt'"
            )

    parser.add_argument(
        "submit_site",
        choices=["unl", "uc", "syr", "ucsd"],
        help="The site from which this workflow is being submitted (e.g. 'unl', 'uc', 'syr', 'ucsd')"
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
                "-c",
                "--corrupt",
                action="append",
                default=[],
                metavar="HOSTNAME",
                help="Host to corrupt. Multiple hosts can be given by specifying"
                " -c <hostname1> -c <hostname2> .."
            )

    parser.add_argument(
                "-t",
                "--timestamps-file",
                help="Path to write timestamp file to."
            )

    parser.add_argument(
                "-m",
                "--corrupt_times",
                default="1",
                type=str,
                help="This is the count that corruption command will be issued, for multiple files corruption"
            )

    parser.add_argument(
                "-p",
                "--corrupt_prob",
                default="1",
                type=str,
                help="The probability of corruption (arg for chaos-jungle)"
            )
    
    parser.add_argument(
                "-x",
                "--populate",
                action="store_true",
                help="Set to enable the pre-population of caches with files used in this workflow"
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
    os.chdir(BASE_DIR)

    # create DIR (1 or more test runs)
    WORK_DIR = Path(args.dir)
    try:
        Path.mkdir(WORK_DIR)
    except FileExistsError:
        # other runs might want to run in this directory
        pass

    assert WORK_DIR.is_dir()
    log.info("test directory set to: {}".format(WORK_DIR))

    # --- Bypass Data Staging --------------------------------------------------
    util.bypass_staging(args.submit_site)

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
        path=str(BASE_DIR / "sites.yml"),
        work_dir=str(WORK_DIR),
        run_id=args.run_id,
        submit_site=args.submit_site
    )

    # --- Transformations - Replicas - Workflow ---------------------------------
    staging_site = "{}-staging.data-plane".format(args.submit_site)
    username = getpass.getuser()
    base_dir = os.getcwd()

    wf = Workflow("01-bypass")

    # transformations
    tc = TransformationCatalog()
    script = Transformation(
                            'job.sh',
                            site='origin',
                            pfn='http://{}/~{}/inputs/job-wrapper.sh'.format(staging_site, username),
                            is_stageable=True,
                            checksum={"sha256":sha256(str(BASE_DIR / "job-wrapper.sh"))}
                        )
    tc.add_transformations(script)

    # a list of common inputs for all jobs
    inputs = []
    urls = []
    rc = ReplicaCatalog()
    for entry in os.listdir(str(Path(BASE_DIR / 'inputs'))):
        infile = File(entry)
        inputs.append(infile)
        chksum = sha256(str(BASE_DIR / 'inputs/{}'.format(entry)))
        pfn = 'http://{}/~{}/inputs/{}'.format(staging_site, username, entry)
        urls.append(pfn)
        rc.add_replica(
                    'origin',
                    infile,
                    pfn,
                    checksum={"sha256": chksum}
                )

    if args.populate:
        # pre populate the caches
        for site in ["syr", "unl", "ucsd", "uc"]:
            proxy = "http://{}-cache:8000".format(site)
            log.info("populating cache at {}".format(site))
            for url in urls:
                util.wget(url, http_proxy=proxy)

    for i in range(args.num_jobs):
        j = Job(script).add_args(i).add_inputs(*inputs)
        wf.add_jobs(j)

    wf.add_transformation_catalog(tc)
    wf.add_replica_catalog(rc)

    if args.timestamps_file:
        with open(args.timestamps_file, "w") as f:
            f.write(datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " START")

    # start driver experiment(s) for the given site(s)
    iris_experiment_drivers = list()
    for site in args.corrupt:
        iris_experiment_drivers.append(
            subprocess.Popen(
                [
                    str(BASE_DIR / "iris-experiment-driver"),
                    site,
                    str(WORK_DIR),
                    args.run_id,
                    args.corrupt_times,
                    args.corrupt_prob
                ]
            )
        )
        log.info("iris-experiment-driver started for site: {}".format(site))

    # start workflow
    try:
        log.info("planning and submitting workflow with {} jobs".format(args.num_jobs))
        wf.plan(
                output_site="local",
                dir=str(WORK_DIR),
                relative_dir=args.run_id,
                sites=["condorpool"],
                staging_sites={"condorpool": "origin"},
                submit=True,
                force=True
        )\
        .wait()

    except PegasusClientError as e:
        log.error(e.output)
    finally:
        # terminate driver experiment(s)
        for ied in iris_experiment_drivers:
            ied.terminate()

        if args.timestamps_file:
            with open(args.timestamps_file, 'a') as f:
                f.write('\n' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " END")

        # ensure pegasus-dagman is down
        util.wait_on_pegasus_dagman()







