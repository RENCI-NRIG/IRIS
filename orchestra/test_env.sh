#!/bin/bash

# modify according to your experiment
export USER="root"
export SSH_OPTION="-i <root private key> -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
export OUTPUT_DIR=/root/iris_results
export WORKFLOW_USER="ericafu"
export ES_USERNAME=""
export ES_PASSWORD=""

# unlikely you will need to change follwing items
export START_RUN=1
export CORRUPT_NODES_FILE=${OUTPUT_DIR}/CORRUPT_NODES
export CORRUPT_EDGES_FILE=${OUTPUT_DIR}/CORRUPT_EDGES
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



