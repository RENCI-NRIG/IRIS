#!/usr/bin/env python3
import argparse
import sys

from util import restart_caches, clear_caches

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Restart and clear caches at the given host(s). "
        "Example: reset_caches.py uc-cache ucsd-cache"
    )

    parser.add_argument(
        "hostnames",
        nargs="+",
        choices=["uc-cache", "unl-cache", "ucsd-cache", "syr-cache"],
        help="One or more hostnames where caches reside"
    )

    args = parser.parse_args()
    args.hostnames = set(args.hostnames)

    return args

if __name__=="__main__":
    args = parse_args()

    clear_caches(*args.hostnames)
    restart_caches(*args.hostnames)


