# 01 Bypass Staging Cache Corrupt 

## Description

This will run a workflow with `N` independent jobs. One or more compute hosts
may be corrupted at given times based on a given probability. Data staging is
bypassed in this experiment (prior to running the workflow, data is manually
staged into `uc-staging`. Additionally, before the workflow is started, the
http caches on the compute sites are prepopulated with all the files needed
by the workflow jobs. 

## Usage
```
usage: workflow.py [-h] [-c HOSTNAME] [-t TIMESTAMPS_FILE] [-m CORRUPT_TIMES]
                   [-p CORRUPT_PROB]
                   dir run_id [1, 1000]

Run a workflow with N independent jobs. Multiple compute hosts may be
corrupted if specified. Example: 'workflow.py /home/ryan/test1 run1 30 -c syr-
compute-c2 -c unl-compute-c1 -t /tmp/iris_timestamps/this_run.txt'

positional arguments:
  dir                   Test directory for this workflow. One will be created
                        if it already does not exist.
  run_id                Run dir that will be created for this workflow in
                        <dir>.
  [1, 1000]             The number of independent workflow jobs to run.

optional arguments:
  -h, --help            show this help message and exit
  -c HOSTNAME, --corrupt HOSTNAME
                        Host to corrupt. Multiple hosts can be given by
                        specifying -c <hostname1> -c <hostname2> ..
  -t TIMESTAMPS_FILE, --timestamps-file TIMESTAMPS_FILE
                        Path to write timestamp file to.
  -m CORRUPT_TIMES, --corrupt_times CORRUPT_TIMES
                        This is the count that corruption command will be
                        issued, for multiple files corruption
  -p CORRUPT_PROB, --corrupt_prob CORRUPT_PROB
                        The probability of corruption (arg for chaos-jungle)
```

## Args Explained

`dir`: An absolute path to a directory where workflow runs (`run_id`) will be placed. 
It will be created if one does not already exist. For example, this could be `/home/tanaka/test1`.

`run_id`: Must be **unique** within `dir`. The Pegasus submit dir for this run will be called `run_id`
and will be placed in `dir`.

`[1, 1000]`: The number of independent pegasus jobs that will be created. Typically 10 - 30 is used
for test runs, and 100 for an actual experiment run.

`-c HOSTNAME`: Which host to corrupt using the `iris-experiment-driver` script defined here. The log
file that is created by this script will be written to `/tmp/iris_corrupt_<HOSTNAME>_<run_id>.log`.
You may specify multiple hosts to corrupt. For example using `-c unl-compute-c1 -c syr-compute-c2`
would cause `iris-experiment-driver` to be executed for both of thoses hosts. Similarly, you will end up
with two log files `/tmp/iris_corrupt_unl-compute-c1_<run_id>.log` and 
`/tmp/iris_corrupt_syr-compute-c2_<run_id>.log`. 

`-t TIMESTAMPS_FILE`: An absolute path to the timestamps file that will be created for this workflow.
For example,  `-t /tmp/timestamps_test1_run1.txt` could be used. 

`-m CORRUPT_TIMES`: The number of times that the corruption command will be executed in `iris-experiment-driver`

`-p CORRUPT_PROB`: The probability of corruption which is passed to `iris-experiment-driver`
as an argument for `chaos-jungle`.

## Example Usage

`./workflow.py /home/tanaka/test_batch0 run1 30`

`./workflow.py /home/tanaka/test_batch1 run1 100 -c syr-compute-c2 -t /tmp/timestamp_test_batch1_run1.txt`

`./workflow.py /home/tanaka/test_batch1 run2 100 -c syr-compute-c2  -c unl-compute-c1 -t /tmp/timestamp_test_batch1_run1.txt`


