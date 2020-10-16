# 02 Network Corrupt

## Description

This will run a workflow with `N` independent jobs. For this workflow, use of
the http caches are disabled and file transfers will take place between the
compute sites and the staging site whenever a job is run. The goal is to have
data flow through as many network links as possible (links will be corrupted based
on the experiment run). To avoid the bypass staging phase failing due to 
network links being corrupted, this part has been placed in its own script.

There are two scripts that should be run when conducting this experiment. Note that
they **should run in the order given here**. The following section explains usage
in further detail.
1. `experiments/workflows/02-network-corrupt/bypass_staging.py`
2. `experiments/workflows/02-network-corrupt/workflow.py`

## Usage

### 1. bypass_staging.py

Bypass staging by Pegasus of files used by jobs (files needed to run this
experiment workflow will be transfered to the staging site by this script).
For example, if the experiment requires that a workflow be submitted
from `uc-submit` and `syr-submit`, prior to workflow submission, 
`./bypass_staging.py uc syr` must be called. This script can be run from
any host. 

```
usage: bypass_staging.py [-h] {uc,unl,ucsd,syr} [{uc,unl,ucsd,syr} ...]

Bypass staging for the given site(s) Example: bypass_staging.py unl uc

positional arguments:
  {uc,unl,ucsd,syr}  One or more hostnames staging should be bypassed

optional arguments:
  -h, --help         show this help message and exit
```

### 2. workflow.py
Run the workflow. This must be run from the intented submit host. For example,
if it is to be run from `uc-submit`, `ssh` to that site, and when calling this script, 
the first positional argument should be `uc`. To allow for multiple workflows to be run, 
at the same time, background this process. 

```
usage: workflow.py [-h] [-t TIMESTAMPS_FILE] {unl,uc,syr,ucsd} dir run_id [1, 1000]

Run a workflow with N independent jobs. Prior to running this workflow, run pre_setup.py to clear and restart the caches, and to do bypass staging.

positional arguments:
  {unl,uc,syr,ucsd}     The site from which this workflow is being submitted (e.g. 'unl', 'uc', 'syr', 'ucsd')
  dir                   Test directory for this workflow. One will be created if it already does not exist.
  run_id                Run dir that will be created for this workflow in <dir>.
  [1, 1000]             The number of independent workflow jobs to run.

optional arguments:
  -h, --help            show this help message and exit
  -t TIMESTAMPS_FILE, --timestamps-file TIMESTAMPS_FILE
                        Path to write timestamp file to.
```

## Example Usage

```
# bypass staging
./experiments/workflows/02-network-corrupt/bypass_staging.py ucsd

# START NETWORK CORRUPT HERE 
# ...
# ..
# .

# run workflow at ucsd-submit
ssh tanaka@ucsd-submit 'python3 ucsd /path/to/workflow.py /home/tanaka/test run1 30 -p -t /tmp/wf1_ts_file'
```