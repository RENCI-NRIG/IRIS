#!/usr/bin/env python3
import sys
import argparse
import pathlib
import subprocess

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Corrupt a given cache. This will fork the iris-experiment-driver "
        " shell script and return immediately. "
        " Example: ./iris-experiment-driver.py unl-cache ucsd -m 3 -p 0.05 -d corrupt_ucsd_files_at_unl.log"
    )

    parser.add_argument(
        "cache",
        choices=["unl-cache", "ucsd-cache", "uc-cache", "syr-cache"],
        help="The cache to corrupt"
    )

    parser.add_argument(
        "submit_site",
        choices=["unl", "ucsd", "uc", "syr"],
        help="The site from which the workflow was submitted."
    )

    parser.add_argument(
        "log_file",
        type=str,
        help="Name of log file that will be used to log corrupt start and end time "
        " and copied to /tmp at the site where corruption occurs."
    )

    parser.add_argument(
        "-m",
        "--corrupt-times",
        default="1",
        type=str,
        help="The number of times corruption will occur."
    )

    parser.add_argument(
        "-p",
        "--corrupt-probability",
        default="1",
        type=str,
        help="The probability of corruption (arg for chaos-jungle) at each time of corruption"
    )

    parser.add_argument(
        "-d",
        "--debug-file",
        type=str,
        default=None,
        help="File to write debug output to"
    )

    return parser.parse_args(args)

if __name__=="__main__":
    args = parse_args()


    proc = subprocess.Popen(
        [
            str(pathlib.Path(__file__).parent.resolve() / "iris-experiment-driver"),
            args.cache,
            args.submit_site,
            args.log_file,
            args.corrupt_times,
            args.corrupt_probability
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    out, err = proc.communicate()

    if args.debug_file:

        with open(args.debug_file, "w") as f:
            if out:
                f.write("stdout\n")
                f.write(out.decode())

            if err:
                f.write("stderr\n")
                f.write(err.decode())
