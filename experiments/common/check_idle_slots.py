#!/usr/bin/env python3
"""
A pre-experiment check to make sure compute resources are ready.
However, this does not garuantee that a job will land on any of
these resources. 

Returns 0 if we get the following expected condor status
else returns 1.

Name            State     Activity
syr-compute-c0  Unclaimed Idle
syr-compute-c1  Unclaimed Idle
uc-compute-c0   Unclaimed Idle
uc-compute-c1   Unclaimed Idle
ucsd-compute-c0 Unclaimed Idle
ucsd-compute-c1 Unclaimed Idle
unl-compute-c0  Unclaimed Idle
unl-compute-c1  Unclaimed Idle
"""
import sys

import htcondor
import classad

def main():
    coll = htcondor.Collector()
    slots = coll.query(
                htcondor.AdTypes.Startd,
                projection=["Name", "Activity", "State"]
            )

    expected_machines = {
                "syr-compute-c0",
                "syr-compute-c1",
                "uc-compute-c0",
                "uc-compute-c1",
                "ucsd-compute-c0",
                "ucsd-compute-c1",
                "unl-compute-c0",
                "unl-compute-c1"
            }

    current_machines = {s["Name"] for s in slots if s["State"] == "Unclaimed" and s["Activity"] == "Idle"}
    if current_machines != expected_machines:
        print("Expected machines not found")
        return 1
    
    print("Expected machines found")
    slots.sort(key=lambda s:s["Name"])
    for s in slots:
        print(repr(s))

    return 0

if __name__=="__main__":
    sys.exit(main())
