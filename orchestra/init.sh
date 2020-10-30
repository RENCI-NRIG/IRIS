#!/bin/bash

source ./test_env.sh
export POSTBOOT_DIR=/var/iris_postboot

set -u
apt install -y python3-pip
pip3 install elasticsearch_dsl
mkdir -p ${OUTPUT_DIR}
cd ${OUTPUT_DIR}; rm *; cd -
rm -rf $POSTBOOT_DIR; mkdir -p $POSTBOOT_DIR; chmod 777 $POSTBOOT_DIR
cp /etc/hosts $POSTBOOT_DIR

sudo -u $WORKFLOW_USER bash -c "cd /home/${WORKFLOW_USER}; git clone https://github.com/RENCI-NRIG/IRIS.git"

## parse the etc/hosts
declare -i isNeucaComet
isNeucaComet=0
while IFS= read -r line
do
    begin=$(cut -d' ' -f 1 <<< $line)
    if [ $isNeucaComet -eq 0 ] && [ "$begin" == "###" ] && [ -z "${line##*comet*}" ]; then
      isNeucaComet=1
    fi
    if [ $isNeucaComet -eq 1 ] && [ "$begin" != "###" ] && [ "$line" != "" ] && [ -z "${line##*'.'*}" ]; then
        echo $line >> $ALL_NODES_FILE
    fi
done < "${POSTBOOT_DIR}/hosts"

## get the interfaces and gw information from all nodes
declare -i exists
exists=0 # use the flag so that re-run this script won't append again
while IFS= read -r line; do
    nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
    node=$(echo $line | awk '{print $2;}'); #echo $node

    if [[ $node == *"submit"* ]]; then
        echo clone IRIS to $node
        ${SSH_CMD} ${WORKFLOW_USER}@${nodeip} "git clone https://github.com/RENCI-NRIG/IRIS.git"
    fi

    ${SSH_CMD} ${WORKFLOW_USER}@${nodeip} "sudo cp /root/tmp_gw ~/"
    ${SSH_CMD} ${WORKFLOW_USER}@${nodeip} "sudo cp /root/tmp_links.sh ~/"
    ${SCP_CMD} ${WORKFLOW_USER}@${nodeip}:tmp_links.sh ${POSTBOOT_DIR}/${node}_links.sh
    ${SCP_CMD} ${WORKFLOW_USER}@${nodeip}:tmp_gw ${POSTBOOT_DIR}/${node}_gw
    if [ -f "${POSTBOOT_DIR}/${node}_gw" ]; then
        router=$(cut -d':' -f 2 <<< $(less ${POSTBOOT_DIR}/${node}_gw))
        echo $node is end node, gw IP:$router
        if [ "$router" != "" ]; then
            echo $line >> $END_NODES_FILE
            if [[ $line == *"cache"* ]]; then
                echo $line >> $CORRUPT_NODES_FILE
            fi
        fi
        anotherIP=$(cut -d'=' -f 2 <<< $(less ${POSTBOOT_DIR}/${node}_links.sh))
        pair=$(echo $anotherIP $node.data-plane)
        if grep -Fxq "$pair" ${POSTBOOT_DIR}/hosts.data-plane
        then
            exists=1
            echo "$pair" exists
        else
            echo "add $pair to /etc/hosts"
            echo $pair >> ${POSTBOOT_DIR}/hosts.data-plane
        fi
    fi
    cat ${POSTBOOT_DIR}/${node}_links.sh >> $ALL_EDGES_FILE
done < $ALL_NODES_FILE

# append hosts.data-plane to /etc/hosts of End Nodes
if [ $exists -eq 0 ]; then
    while IFS= read -r line; do
        node=$(echo $line | awk '{print $2;}'); #echo $node
        ${SCP_CMD} ${POSTBOOT_DIR}/hosts.data-plane ${WORKFLOW_USER}@${node}:/tmp/
        ${SSH_CMD} ${WORKFLOW_USER}@${node} "sudo bash -c 'cat /tmp/hosts.data-plane >> /etc/hosts'"
    done < $END_NODES_FILE
fi

# generate NODE_ROUTER_FILE
_get_hostname_by_dataplane_IP () {
    while IFS= read line || [ -n "$line" ]
    do
        x_ip=$(cut -d= -f2 <<< $line)
        if [ $x_ip == $1 ]; then
            RETURN_HOSTNAME=$(cut -d' ' -f2 <<< $line | cut -d_ -f1)
            break
        fi
    done < ${ALL_EDGES_FILE}
}

for file in $(ls $POSTBOOT_DIR); do
if [ -z "${file##*'_gw'*}" ]; then
  while IFS= read line || [ -n "$line" ]
  do
      node=$(cut -d: -f1 <<< $line)
      routerip=$(cut -d: -f2 <<< $line)
      if [ ! -z $routerip ]; then
        _get_hostname_by_dataplane_IP $routerip
        echo $node $RETURN_HOSTNAME >> ${POSTBOOT_DIR}/${NODE_ROUTER_FILE}
      fi
  done < ${POSTBOOT_DIR}/${file}
fi
done
cat ${POSTBOOT_DIR}/${NODE_ROUTER_FILE}

#cp $END_NODES_FILE $CORRUPT_NODES_FILE
cp $ALL_EDGES_FILE $CORRUPT_EDGES_FILE

cp ${POSTBOOT_DIR}/${NODE_ROUTER_FILE} ${OUTPUT_DIR}/${NODE_ROUTER_FILE}

