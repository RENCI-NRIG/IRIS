# 02 Network Corrupt

## Usage
```
usage: workflow.py [-h] [-t TIMESTAMPS_FILE] dir run_id [1, 1000]

Run a workflow with N independent jobs. Prior to running this workflow, run
pre_setup.py to clear and restart the caches, and to do bypass staging.

positional arguments:
  dir                   Test directory for this workflow. One will be created
                        if it already does not exist.
  run_id                Run dir that will be created for this workflow in
                        <dir>.
  [1, 1000]             The number of independent workflow jobs to run.

optional arguments:
  -h, --help            show this help message and exit
  -t TIMESTAMPS_FILE, --timestamps-file TIMESTAMPS_FILE
                        Path to write timestamp file to.
```

### Args Explained

`dir`: An absolute path to a directory where workflow runs (`run_id`) will be placed. 
It will be created if one does not already exist. For example, this could be `/home/tanaka/test1`.

`run_id`: Must be **unique** within `dir`. The Pegasus submit dir for this run will be called `run_id`
and will be placed in `dir`.

`[1, 1000]`: The number of independent pegasus jobs that will be created. Typically 10 - 30 is used
for test runs, and 100 for an actual experiment run.

`-t TIMESTAMPS_FILE`: An absolute path to the timestamps file that will be created for this workflow.
For example,  `-t /tmp/timestamps_test1_run1.txt` could be used. 

### Example Usage
Running a simple test.
```
./pre_setup.py
./workflow.py /home/tanaka/test_batch0 run1 30
```

Running a network corruption experiment.
```
./pre_setup.py

# Start network corruption here

./workflow.py /home/tanaka/test_batch0 run2 100 -t /tmp/net_corrupt_run1_timestamps.txt
```


