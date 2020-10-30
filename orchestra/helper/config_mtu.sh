#!/bin/bash

source ./test_env.sh
source ./include.sh
_get_all_nodes
set -u

## get the interfaces and gw information from all nodes
for v_nodeip in $ALL_NODES
do
    echo $v_nodeip
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens6 mtu 1500"
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens7 mtu 1500"
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens8 mtu 1500"
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens9 mtu 1500"
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens10 mtu 1500"
    ${SSH_CMD} ${v_nodeip} "sudo ifconfig ens11 mtu 1500"
done