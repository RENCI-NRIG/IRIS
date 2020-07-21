#!/bin/bash
set -u

source ./test_env.sh
source ./include.sh
_get_corrupt_nodes
_get_corrupt_edges
#_get_end_nodes

echo "CORRUPT_NODES:" $CORRUPT_NODES
echo "CORRUPT_EDGES:" $CORRUPT_EDGES

if [ -f ${OUTPUT_DIR}/revert_previous.sh ]; then
    ${OUTPUT_DIR}/revert_previous.sh
    rm ${OUTPUT_DIR}/revert_previous.sh
fi

currenttime=$(date +"%Y%m%d_%H%M%p")
RESULT_DIR=${OUTPUT_DIR}/output_${currenttime}
WORKFLOW_RESULT_DIR=${WORKFLOW_RESULT_BASE}/${currenttime}
mkdir $RESULT_DIR
cp ${OUTPUT_DIR}/${NODE_ROUTER_FILE} ${RESULT_DIR}/${NODE_ROUTER_FILE}

run=$((START_RUN-1))
if [ $run == 0 ]
then
  # ${RESULT_DIR}/$(basename ${RESULT_DIR}).txt
  if [ -f ${RESULT_DIR}/${RUN_LINKLABEL_FILE} ]; then
    rm ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
  fi
  touch ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
fi

ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit "mkdir -p ${WORKFLOW_RESULT_BASE}"

##### experiment starts ######
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_start

# corrupt storage in CORRUPT_NODES
for v_nodeip in $CORRUPT_NODES
do
  run=$((run+1))
  echo; echo "### New Run" run${run}
  _get_hostname $v_nodeip
  v_node=$RETURN_HOSTNAME
  echo "Corrupting" $v_node
  echo "run$run $v_node" >> ${RESULT_DIR}/${RUN_LINKLABEL_FILE}

  _get_storage_corrupt_times $v_nodeip
  _get_storage_probablity $v_nodeip

  # Running Workflow, and get the timestamp and corruption log
  command="python3 ${WORKFLOW_BASE_DIR}/${STORAGE_WORKFLOW_ID}/workflow.py ${WORKFLOW_RESULT_DIR} run${run} ${JOB_NUMBER} -c ${v_node} -t ${WORKFLOW_RESULT_DIR}/run${run}_timestamps -m ${CORRUPT_TIMES} -p ${STORAGE_PROB}"
  echo ${command}
  ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit ${command}
  scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:${WORKFLOW_RESULT_DIR}/run${run}_timestamps ${RESULT_DIR}/run${run}_timestamps
  scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:${WORKFLOW_RESULT_DIR}/${v_node}_run${run}_corrupt.log ${RESULT_DIR}/${v_node}_run${run}_corrupt.log
  scp $SSH_OPTION root@${v_node}:/var/log/cj.log ${RESULT_DIR}/${v_node}_run${run}_cj.log
done


# corrupt network in CORRUPT_EDGES
while IFS= read line || [ -n "$line" ]
do
    if [[ $line = \#* ]] ; then
      continue;
    fi

    if [ $run != 0 ]; then
      sleep 60
    fi

    # parse link and packet-corrupt-rate P
    link=$(cut -d' ' -f2 <<< $line | cut -d= -f1)
    corrupt_rate=$NW_CORRUPT_RATE
    P=$(cut -d' ' -f3 <<< $line)
    if [ ! -z $P ]; then
        corrupt_rate=$P
    fi
    if [ $corrupt_rate != "0" ]; then
      param_I=$(echo "1 / $corrupt_rate" | bc)
    fi

    run=$((run+1))
    echo; echo "### New Run" run${run}

    ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit python3 ${WORKFLOW_BASE_DIR}/${NETWORK_WORKFLOW_ID}/pre_setup.py

    echo "Corrupting" $link
    node="$(cut -d'_' -f 1 <<< $link)"
    _get_linkIP $link; linkip=$RETURN_IP

    ssh -n $SSH_OPTION ${USER}@${node} ifconfig | grep $linkip
    LINE=$(ssh -n $SSH_OPTION ${USER}@${node} ifconfig | grep $linkip -n | awk -F ':' '{print $1}')
    LINE=$((LINE-1))
    interface=$(ssh -n $SSH_OPTION ${USER}@${node} ifconfig | awk NR==${LINE} | awk -F ':' '{print $1}')

    # corrupt the LINK(E_EDGE) by sudo ./xdp_flow_modify.py
    # _get_network_probablity $link
    echo "corrupt_rate=${corrupt_rate} (1/${param_I})"
    if [ $param_I != "0" ]; then
      echo "run$run $link $corrupt_rate" >> ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
      ssh -n $SSH_OPTION ${USER}@${node} sudo $CJ_DIR/bpf/bcc/xdp_flow_modify.py -i $param_I -t ${interface} > /dev/null 2>&1 &
      sleep 2
      echo $link : $interface ${linkip}
      link_corrupt_log=${RESULT_DIR}/${link//_/.}+${corrupt_rate}_run${run}_corrupt.log
      echo $(date +%s) CORRUPT_START "${link//_/.}" > ${link_corrupt_log}
      ssh -n $SSH_OPTION ${USER}@${node} ps ax | grep xdp_flow | grep -v sudo | grep -v grep

      # create revert_previous.sh for later use:
      cat <<EOF >>${OUTPUT_DIR}/revert_previous.sh
#!/bin/bash
set -u
echo reverting ${link}
ssh -n $SSH_OPTION ${USER}@${node} sudo $CJ_DIR/bpf/bcc/xdp_flow_modify.py --stoptc ${interface}
sleep 2
ssh -n $SSH_OPTION ${USER}@${node} sudo pkill -u root -f xdp_flow_modify
sleep 2
echo ${interface} ${linkip} reverted
ssh -n $SSH_OPTION ${USER}@${node} ps ax | grep xdp_flow | grep -v sudo | grep -v grep
EOF
      chmod u+x ${OUTPUT_DIR}/revert_previous.sh
    fi

    # Running Workflow, and get the timestamp and corruption log
    command="python3 ${WORKFLOW_BASE_DIR}/${NETWORK_WORKFLOW_ID}/workflow.py ${WORKFLOW_RESULT_DIR} run${run} ${JOB_NUMBER} -t ${WORKFLOW_RESULT_DIR}/run${run}_timestamps"
    echo ${command}
    ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit ${command}
    scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:${WORKFLOW_RESULT_DIR}/run${run}_timestamps ${RESULT_DIR}/run${run}_timestamps
 
    #ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit python3 /home/${WORKFLOW_USER}/IRIS/experiments/run.py ${currenttime} run${run} 01-bypass
    #scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:/tmp/iris_timestamps ${RESULT_DIR}/run${run}_timestamps

    # kill the cj network corrupter process and log the time
    if [ $param_I != "0" ]; then
      ${OUTPUT_DIR}/revert_previous.sh
      rm ${OUTPUT_DIR}/revert_previous.sh
      echo $(date +%s) CORRUPT_END "${link//_/.}" >> ${link_corrupt_log}
    fi
done < ${CORRUPT_EDGES_FILE}
sleep 60

# get elastic search csv file
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_end
python3 /root/IRIS/es/iris-es-to-ml.py -s $(cat ${RESULT_DIR}/ts_start) -e $(cat ${RESULT_DIR}/ts_end)
mv transfer-events.csv ${RESULT_DIR}/transfer-events.csv
python3 iris_gen_result.py $RESULT_DIR
