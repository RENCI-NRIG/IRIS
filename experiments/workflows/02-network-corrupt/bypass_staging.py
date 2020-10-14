#!/usr/bin/env python3
import logging
import sys
import argparse

from pathlib import Path

################################################################################
######### using IRIS/experiments/common and pegasus-config setup ###############
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "common"))

import util

sys.path.append(util.pegasus_config_python())
################################################################################

logging.basicConfig(level=logging.DEBUG)

wf_exeriment_dir = Path(__file__).parent.resolve()

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Bypass staging for the given site(s) "
        " Example: bypass_staging.py unl-staging uc-staging"
    )

    parser.add_argument(
        "hostnames",
        nargs="+",
        choices=["uc-staging", "unl-staging", "ucsd-staging", "syr-staging"],
        help="One or more hostnames staging should be bypassed"
    )

    args = parser.parse_args()
    args.hostnames = set(args.hostnames)

    return args

if __name__=="__main__":
    args = parse_args()

    for site in args.hostnames:
        util.bypass_staging(wf_experiment_dir, site)
