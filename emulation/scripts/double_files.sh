#!/bin/bash
set -ux

source ./test_env.sh
source $ALL_EDGES_FILE
source ./include.sh

# issue cmds to all nodes
for nodeip in $ALL_NODES; do
   echo ${nodeip}
   # by default , {TEMPLATE_DIR}/00/ has 446 files.
   # use this file to double the files or modify the script to increase the files as you wish
   ssh -n $SSH_OPTION ${USER}@${nodeip} "cp -r ${TEMPLATE_DIR}/00/* ${TEMPLATE_DIR}/01"
done