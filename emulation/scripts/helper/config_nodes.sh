#!/bin/bash
set -ux

source ./test_env.sh
source $ALL_EDGES_FILE
source ./include.sh

# issue cmds to all nodes
for nodeip in $ALL_NODES; do
   echo ${nodeip}
   #ssh -n $SSH_OPTION ${USER}@${nodeip} "cp -r ${TEMPLATE_DIR}/00/* ${TEMPLATE_DIR}/01"
done