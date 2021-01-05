#!/bin/bash

source ../test_env.sh
source ../include.sh
_get_all_nodes
set -uex

## get the interfaces and gw information from all nodes
for v_nodeip in $END_NODES
do
    echo $v_nodeip
    _get_hostname $v_nodeip
    v_node=$RETURN_HOSTNAME
    echo $v_node
    ${SSH_CMD} ${v_nodeip} "sudo hostnamectl set-hostname ${v_node}"
done