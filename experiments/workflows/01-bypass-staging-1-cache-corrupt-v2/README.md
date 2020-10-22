# 01 Bypass Staging Cache Corrupt Experiment

## Description
Run a workflow with `N` independent jobs. One or more compute hosts may be 
corrupted. Data staging is bypassed in this experiment (prior to running the
workflow, data is manually staged into a site specific staging site). 
Before the workflow is started, the HTTP caches at each site can optionally
be prepopulated with all the files needed by the workflow jobs. 

There are three scripts that should be run when conducting this experiment. Note
that they **should be run in the order given here**. The following section explains
usage in further detail.
1. `experiments/common/reset_caches.py`
2. `experiments/workflows/01-bypass-staging-1-cache-corrupt-v2/iris_experiment_driver.py`
3. `experiments/workflows/01-bypass-staging-1-cache-corrupt-v2/workflow.py`

## Usage

### 1. reset_caches.py
Restart 1 or more caches, and clear their contents (located in `/cache`). This
can be run from any host.

```
usage: reset_caches.py [-h] {uc-cache,unl-cache,ucsd-cache,syr-cache} [{uc-cache,unl-cache,ucsd-cache,syr-cache} ...]

Restart and clear caches at the given host(s). Example: reset_caches.py uc-cache ucsd-cache

positional arguments:
  {uc-cache,unl-cache,ucsd-cache,syr-cache}
                        One or more hostnames where caches reside

optional arguments:
  -h, --help            show this help message and exit
```

### 2. iris_experiment_driver.py
Corrupt 1 or more files a the given cache that have been obtained from a given
staging site. For example, running `./iris-experiment-driver.py unl-cache ucsd -m 3 -p 1 -d corrupt_ucsd_files_at_unl.log` 
Means, **corrupt 3 files** at **unl-cache** which were obtained from **ucsd**. `CORRUPT_TIMES`
and `CORRUPT_PROBABILITY` both default to `1`. Corruption does not begin until 
all files needed for jobs from the given source (in this example `unl-cache`) arrive in the
cache (due to cache pre-population or a job needing some file). A check for these files occurs every
second, so corruption is expected to begin within a second of files arriving in the cache.
**Corruption is  hard coded to last for a minute**. Following that, the cache will be cleared. 

This can be run from any host. To corrupt multiple caches, call this script multiple
times. **One caveat is that you need to background each process so that the workflow
execution can start while this runs.** (e.g. `./iris-experiment-driver.py unl-cache ucsd -m 3 -p 1 -d corrupt_ucsd_files_at_unl.log &`)

```
usage: iris_experiment_driver.py [-h] [-m CORRUPT_TIMES] [-p CORRUPT_PROBABILITY] [-l LENGTH] [-d DEBUG_FILE] {unl-cache,ucsd-cache,uc-cache,syr-cache} {unl,ucsd,uc,syr} log_file

Corrupt a given cache. This will fork the iris-experiment-driver and wait for it to complete. Example: ./iris-experiment-driver.py unl-cache ucsd -l 120 -m 3 -p 0.05 -d corrupt_ucsd_files_at_unl.log

positional arguments:
  {unl-cache,ucsd-cache,uc-cache,syr-cache}
                        The cache to corrupt
  {unl,ucsd,uc,syr}     The site from which the workflow was submitted.
  log_file              Name of log file that will be used to log corrupt start and end time and copied to /tmp at the site where corruption occurs.

optional arguments:
  -h, --help            show this help message and exit
  -m CORRUPT_TIMES, --corrupt-times CORRUPT_TIMES
                        The number of times corruption will occur.
  -p CORRUPT_PROBABILITY, --corrupt-probability CORRUPT_PROBABILITY
                        The probability of corruption (arg for chaos-jungle) at each time of corruption
  -l LENGTH, --length LENGTH
                        Duration of corruption in seconds, defaults to 60
  -d DEBUG_FILE, --debug-file DEBUG_FILE
                        File to write debug output to
```

### 3. workflow.py
Run the workflow. This must be run from the intented submit host. For example,
if it is to be run from `uc-submit`, `ssh` there and when calling this script, 
the first positional argument should be `uc`. To allow for multiple workflows to be run, 
at the same time, background this process.

```
usage: workflow.py [-h] [-t TIMESTAMPS_FILE] [-p] {unl,uc,syr,ucsd} dir run_id [1, 1000]

Run a workflow with N independent jobs. Multiple compute hosts may be corrupted if specified. Example: 
'workflow.py unl /home/ryan/test1 run1 30 -p -t timestamp_file.txt

positional arguments:
  {unl,uc,syr,ucsd}     The site from which this workflow is being submitted (e.g. 'unl', 'uc', 'syr', 'ucsd')
  dir                   Test directory for this workflow. One will be created if it already does not exist.
  run_id                Run dir that will be created for this workflow in <dir>.
  [1, 1000]             The number of independent workflow jobs to run.

optional arguments:
  -h, --help            show this help message and exit
  -t TIMESTAMPS_FILE, --timestamps-file TIMESTAMPS_FILE
                        Path to write timestamp file to.
  -p, --populate        Set to enable the pre-population of caches with files used in this workflow
```

## Example Usage

```
#!/bin/bash

# some setup 
# ....
# ...

# reset all caches 
./experiments/common/reset_caches.py uc-cache unl-cache ucsd-cache syr-cache

# enable cache corruption for two caches
./experiments/workflows/01-bypass-staging-1-cache-corrupt-v2/iris_experiment_driver.py unl-cache ucsd -m 7 -p 1 &
./experiments/workflows/01-bypass-staging-1-cache-corrupt-v2/iris_experiment_driver.py syr-cache ucsd -m 7 -p 1 &

# start two workflows
# this workflow will be affected by corrupted files
ssh tanaka@ucsd-submit 'python3 /path/to/workflow.py ucsd /home/tanaka/test run1 30 -p -t wf1_ts_file' &

# this workflow will not be affected by corrupted files 
ssh tanaka@unl-submit 'python3 /path/to/workflow.py unl /home/tanaka/test run1 30 -p -t wf1_ts_file' &

# TODO: add func to check that all submited workflows part of this experiment run are complete
Maybe do something like this (https://stackoverflow.com/questions/356100/how-to-wait-in-bash-for-several-subprocesses-to-finish-and-return-exit-code-0)?

# run processes and store pids in array
for i in $n_procs; do
    ./procs[${i}] &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done
```