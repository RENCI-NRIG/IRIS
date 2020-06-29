#!/bin/bash

# modify according to your experiment
export NW_CORRUPT_RATE=0.006 # default corruption rate for network interface
export JOB_NUMBER=100
export STORAGE_WORKFLOW_ID=01-bypass-staging-1-cache-corrupt-v2
export NETWORK_WORKFLOW_ID=02-network-corrupt

# modify according to your environment
export ES_USERNAME=""
export ES_PASSWORD=""
export SSH_OPTION="-i <private key> -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

export WORKFLOW_USER="ericafu"
export WORKFLOW_BASE_DIR=/home/${WORKFLOW_USER}/IRIS/experiments/workflows
export WORKFLOW_RESULT_BASE=/home/${WORKFLOW_USER}/workflow-runs

export USER="root" # use root user to corrupt
export OUTPUT_DIR=/root/iris_results
export CORRUPT_NODES_FILE=${OUTPUT_DIR}/CORRUPT_NODES
export CORRUPT_EDGES_FILE=${OUTPUT_DIR}/CORRUPT_EDGES

# unlikely you will need to change follwing items
export START_RUN=1
export ALL_EDGES_FILE=${OUTPUT_DIR}/edges_all.sh
export ALL_NODES_FILE=${OUTPUT_DIR}/nodes_all
export END_NODES_FILE=${OUTPUT_DIR}/nodes_end

# do not modify below
export NODE_ROUTER_FILE="node_router"
export RUN_LINKLABEL_FILE=run_label_autogen
export RETURN_HOSTNAME=""
export RETURN_IP=""
export CJ_DIR=/root/chaos-jungle

# to be remove later
export SITE_DIR=/var/www/iris      #if you modify this 000-default.conf will need to be modified as well
export IRIS_DIR=/root/iris
export TEMPLATE_DIR=${IRIS_DIR}/testdata/20190425T121649-0700
export SRC_NODES_FILE=${OUTPUT_DIR}/NODES_SRC
export DEST_NODES_FILE=${OUTPUT_DIR}/NODES_DEST
export maxtransfer=6 # max transfers that can be triggered at the same time



