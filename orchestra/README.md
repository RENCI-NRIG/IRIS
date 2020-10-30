# IRIS workflow experiment

The scripts are expected to run on the Control node under root

### [Before Starting]
Before starting experiments, configuration needs to be modified first.

#### Download the scripts from github
```
$ git clone https://github.com/RENCI-NRIG/IRIS.git
$ cd IRIS/orchestra
```

#### Modify configurations in `test_env.sh`
```
export WORKFLOW_USER=""
export ES_USERNAME=""
export ES_PASSWORD=""
```

#### RUN once `init.sh` to get the topology information (IP addresses of Nodes, Links...) to control machine

```
$ ./init.sh
```


### [Start Experiment]

#### 1. Review and modify `CORRUPT_NODES` and `CORRUPT_EDGES` files in the $OUTPUT_DIR to indicate which nodes and edges to corrupt.
&nbsp;&nbsp;&nbsp;&nbsp;Default all cache nodes and all edges will be included.

&nbsp;&nbsp;&nbsp;&nbsp;in `CORRUPT_NODES` file:

```
199.165.75.188 syr-cache
199.165.75.193 unl-cache
199.165.75.224 ucsd-cache
199.165.75.223 uc-cache
```

&nbsp;&nbsp;&nbsp;&nbsp;in `CORRUPT_EDGES` file:

```
export syr-router-n2_Link26=192.168.26.2
export syr-router-n2_Link24=172.16.24.3
export uc-staging_Link19=192.168.19.3
...
...
```

Every line in these files will become one run of workflow experiment


#### 2. Start the experiment by `wf_experiment01.sh`, a result folder will be created under `OUTPUT_DIR` (i.e. /var/iris_results).
```
$ ./wf_experiment01.sh > ~/console.log 2>&1
```

<br>
Or using following command to test just 1 run of each corruption type.

```
$ ./wf_experiment01.sh --test 1
```

#### 3. Check the latest folder under $OUTPUT_DIR (default:/var/iris_results) for the result

Fields in the output matrix:

```
root_xwf_id
job_id
start_time
end_time
submit_host
submit_user
execution_host
execution_user
job_type
job_exit_code
bytes
lfn
src_label
src_url
src_proto_host
dst_label
dst_url
dst_proto_host
transfer_success
checksum_success
actual_checksum
expected_checksum
scenario
corrupt_label: added by the orchestra script
```
