#!/bin/bash

_get_all_nodes () {
    ALL_NODES=""
    while IFS= read line || [ -n "$line" ]
    do
        nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
        ALL_NODES=${ALL_NODES}' '${nodeip}
    done < ${ALL_NODES_FILE}
}

_get_end_nodes () {
    END_NODES=""
    end_nodes_count=0
    while IFS= read line || [ -n "$line" ]
    do
        nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
        node=$(echo $line | awk '{print $2;}')
        echo $node > $OUTPUT_DIR/${nodeip}_hostname
        END_NODES=${END_NODES}' '${nodeip}
        END_NODES_ARRAY[${end_nodes_count}]=${nodeip}
        end_nodes_count=$((end_nodes_count+1))
    done < ${END_NODES_FILE}
}

_get_src_nodes () {
    SRC_NODES=""
    while IFS= read line || [ -n "$line" ]
    do
        if [[ $line = \#* ]] ; then
          continue;
        fi
        nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
        SRC_NODES=${SRC_NODES}' '${nodeip}
    done < ${SRC_NODES_FILE}
}

_get_dest_nodes () {
    DEST_NODES=""
    while IFS= read line || [ -n "$line" ]
    do
        if [[ $line = \#* ]] ; then
          continue;
        fi
        nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
        DEST_NODES=${DEST_NODES}' '${nodeip}
    done < ${DEST_NODES_FILE}
}

_get_corrupt_nodes () {
    CORRUPT_NODES=""
    while IFS= read line || [ -n "$line" ]
    do
        if [[ $line = \#* ]] ; then
          continue;
        fi
        nodeip=$(echo $line | awk '{print $1;}'); #echo $nodeip
        CORRUPT_NODES=${CORRUPT_NODES}' '${nodeip}
    done < ${CORRUPT_NODES_FILE}
}

_get_all_edges () {
    ALL_EDGES=""
    while IFS= read line || [ -n "$line" ]
    do
        edge=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
        ALL_EDGES=${ALL_EDGES}' '${edge}
    done < ${ALL_EDGES_FILE}
}

_get_corrupt_edges () {
    CORRUPT_EDGES=""
    while IFS= read line || [ -n "$line" ]
    do
        if [[ $line = \#* ]] ; then
          continue;
        fi
        edge=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
        CORRUPT_EDGES=${CORRUPT_EDGES}' '${edge}
        #echo CORRUPT_EDGES ${CORRUPT_EDGES}
    done < ${CORRUPT_EDGES_FILE}
}

_get_ip () {
    while IFS= read line || [ -n "$line" ]
    do
        x_node=$(cut -d' ' -f2 <<< $line)
        if [ $x_node == $1 ]; then
            RETURN_IP=$(cut -d' ' -f1 <<< $line)
            break
        fi
    done < ${ALL_NODES_FILE}
}

_get_hostname () {
  x_ip=$1
  RETURN_HOSTNAME=$(head -n 1 $OUTPUT_DIR/${x_ip}_hostname)
  #echo "RETURN_HOSTNAME = $RETURN_HOSTNAME"
}

_get_virtualIP () {
    while IFS= read line || [ -n "$line" ]
    do
        edge=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
        x_node=$(cut -d_ -f1 <<< $edge)
        if [ $x_node == $1 ]; then
            RETURN_IP=$(cut -d= -f2 <<< $line)
            break
        fi
    done < ${ALL_EDGES_FILE}
}


_get_linkIP () {
    while IFS= read line || [ -n "$line" ]
    do
        edge=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
        if [ $edge == $1 ]; then
            RETURN_IP=$(cut -d= -f2 <<< $line)
            break
        fi
    done < ${ALL_EDGES_FILE}
}


_get_hostname_by_virtualIP () {
    while IFS= read line || [ -n "$line" ]
    do
        x_ip=$(cut -d= -f2 <<< $line)
        if [ $x_ip == $1 ]; then
            RETURN_HOSTNAME=$(cut -d' ' -f2 <<< $line | cut -d_ -f1)
            break
        fi
    done < ${ALL_EDGES_FILE}
}

_get_storage_corrupt_times () {
    CORRUPT_TIMES=1
    while IFS= read line || [ -n "$line" ]
    do
      x_ip=$(cut -d' ' -f1 <<< $line)
        if [ $x_ip == $1 ]; then
          P=$(cut -d' ' -f3 <<< $line)
          if [ ! -z $P ]; then
            CORRUPT_TIMES=$P
            echo "CORRUPT_TIMES=$CORRUPT_TIMES"
          fi
        break
      fi
    done < ${CORRUPT_NODES_FILE}
}

_get_storage_probablity () {
    STORAGE_PROB=1
    while IFS= read line || [ -n "$line" ]
    do
      x_ip=$(cut -d' ' -f1 <<< $line)
        if [ $x_ip == $1 ]; then
          P=$(cut -d' ' -f4 <<< $line)
          echo "P=$P"
          if [ ! -z $P ]; then
            STORAGE_PROB=$P
            echo "STORAGE_PROB=$STORAGE_PROB"
          fi
        break
      fi
    done < ${CORRUPT_NODES_FILE}
}

_get_network_probablity () {
    NETWORK_PROB=0.002
    while IFS= read line || [ -n "$line" ]
    do
      x_link=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
        if [ $x_link == $1 ]; then
          P=$(cut -d' ' -f3 <<< $line)
          echo "P=${P}"
          if [ ! -z $P ]; then
            NETWORK_PROB=$P
          fi
        break
      fi
    done < ${CORRUPT_EDGES_FILE}
    echo $NETWORK_PROB
    if [ $NETWORK_PROB != "0" ]; then
      NETWORK_PROB=$(echo "1 / $NETWORK_PROB" | bc)
    fi
}

_generate_node_router_file () {
  for file in $(ls $OUTPUT_DIR); do
    if [ -z "${file##*'_gw'*}" ]; then
      while IFS= read line || [ -n "$line" ]
      do
          node=$(cut -d: -f1 <<< $line)
          routerip=$(cut -d: -f2 <<< $line)
          if [ ! -z $routerip ]; then
            _get_hostname_by_virtualIP $routerip
            echo $node $RETURN_HOSTNAME >> ${OUTPUT_DIR}/${NODE_ROUTER_FILE}
          fi
      done < ${OUTPUT_DIR}/${file}
    fi
  done
  cat ${OUTPUT_DIR}/${NODE_ROUTER_FILE}
}

_get_end_nodes
_get_all_nodes
_get_all_edges
#echo END_NODES = $END_NODES
#echo ALL_NODES = $ALL_NODES
#echo ALL_EDGES = $ALL_EDGES

