#!/bin/bash
set -u

source ./test_env.sh
source ./include.sh
_get_corrupt_nodes
_get_corrupt_edges
#_get_end_nodes

echo "CORRUPT_NODES:" $CORRUPT_NODES
echo "CORRUPT_EDGES:" $CORRUPT_EDGES

sites=("uc" "syr" "ucsd" "unl")
#sites=("uc" "syr")
n_sites=${#sites[@]}
echo "n_sites= " $n_sites

if [ -f ${OUTPUT_DIR}/revert_previous.sh ]; then
    ${OUTPUT_DIR}/revert_previous.sh
    rm ${OUTPUT_DIR}/revert_previous.sh
fi

currenttime=$(date +"%Y%m%d_%H%M%p")
RESULT_DIR=${OUTPUT_DIR}/${RESULT_PREFIX}_${currenttime}   # in control node
WORKFLOW_RESULT_DIR=${WORKFLOW_RESULT_BASE}/${currenttime} # in submit node
mkdir $RESULT_DIR
cp ${OUTPUT_DIR}/${NODE_ROUTER_FILE} ${RESULT_DIR}/${NODE_ROUTER_FILE}

run=$((START_RUN-1))
if [ $run == 0 ]
then
  # create new label file
  if [ -f ${RESULT_DIR}/${RUN_LINKLABEL_FILE} ]; then
    rm ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
  fi
  touch ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
fi

#set -ux

for (( i=0; i<$n_sites; i++ ));
do
  site=${sites[$i]}
  ssh -n $SSH_OPTION ${WORKFLOW_USER}@${site}-submit "mkdir -p ${WORKFLOW_RESULT_BASE}"
done

##### experiment starts ######
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_start

# corrupt caches in CORRUPT_NODES
for v_nodeip in $CORRUPT_NODES
do
  
  run=$((run+1))
  echo; echo "### New Run" run${run}
  _get_hostname $v_nodeip
  v_node=$RETURN_HOSTNAME
  echo "Corrupting" $v_node

  _get_storage_corrupt_times $v_nodeip
  _get_storage_probablity $v_nodeip

  echo "run$run $v_node ${CORRUPT_TIMES} ${STORAGE_PROB}" >> ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
    
  # clear caches
  cmd1="sudo -u $WORKFLOW_USER python3 /home/${WORKFLOW_USER}/IRIS/experiments/common/reset_caches.py uc-cache unl-cache ucsd-cache syr-cache"
  ${cmd1}
  echo $cmd1

  # backup and clear cj.log so later we get a clean one
  ssh $SSH_OPTION root@${v_node} "cp /var/log/cj.log /var/log/cj_${currenttime}.log"
  ssh $SSH_OPTION root@${v_node} "rm /var/log/cj.log"

  # randomly pick one victim as the corrupt_src, 
  # and start cache corruption in background.
  corrupt_src=${sites[$(( $RANDOM % $n_sites ))]}
  echo "corrupt_src =" $corrupt_src

  CORRUPT_TS_FILE=/tmp/${v_node}_run${run}_corrupt.log
  cmd1="sudo -u $WORKFLOW_USER python3 ${WORKFLOW_BASE_DIR}/${STORAGE_WORKFLOW_ID}/iris_experiment_driver.py ${v_node} ${corrupt_src} ${CORRUPT_TS_FILE} -m ${CORRUPT_TIMES} -p ${STORAGE_PROB}"
  $(${cmd1}) &
  echo $cmd1; sleep 5

  # start workflow from each submit node
  for (( i=0; i<$n_sites; i++ ));
  do
    site=${sites[$i]}; echo "for site ${site}:"

    cmd_wf="python3 ${WORKFLOW_BASE_DIR}/${STORAGE_WORKFLOW_ID}/workflow.py ${site} ${WORKFLOW_RESULT_DIR} run${run} ${JOB_NUMBER} --populate -t ${WORKFLOW_RESULT_DIR}/run${run}_timestamps"
    echo ${cmd_wf}
    ssh -n $SSH_OPTION ${WORKFLOW_USER}@${site}-submit ${cmd_wf} > ${RESULT_DIR}/run${run}_${site}_console.out 2>&1 &
    sleep 15
  done

  echo "wait at least 5 mins before checking"
  sleep 300

  # make sure the workflow process in each submit site has finished
  # and get the timestamp file from each site
  for (( i=0; i<$n_sites; i++ ));
  do
    site=${sites[$i]}
    while [[ -n $(ssh -n $SSH_OPTION ${WORKFLOW_USER}@${site}-submit ps ax | grep workflow.py) ]]; do
        echo " workflows ongoing in ${site}-submit ..."
        sleep 15
    done
    scp $SSH_OPTION ${WORKFLOW_USER}@${site}-submit:${WORKFLOW_RESULT_DIR}/run${run}_timestamps ${RESULT_DIR}/run${run}_${site}_timestamps
  done

  # make sure the corruption process has finished
  # and collect the corruption logs of driver and Chaos Jungle
  while [[ -n $(ps ax | grep iris_experiment_driver.py | grep -v sudo | grep -v grep) ]]; do
    echo " corruption ongoing"
    sleep 5
  done
  scp $SSH_OPTION root@${v_node}:/var/log/cj.log ${RESULT_DIR}/${v_node}_run${run}_cj.log
  mv ${CORRUPT_TS_FILE} ${RESULT_DIR}/

done


# corrupt network in CORRUPT_EDGES
while IFS= read line || [ -n "$line" ]
do
    if [[ $line = \#* ]] ; then
      continue;
    fi

    if [ $run != 0 ]; then
      sleep 30
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

    # invoke bypass staging script before starting corruption and workflow
  for i in ${!sites[@]};
  do
    site=${sites[$i]}
    ssh -n $SSH_OPTION ${WORKFLOW_USER}@${site}-submit python3 ${WORKFLOW_BASE_DIR}/${NETWORK_WORKFLOW_ID}/bypass_staging.py $site
  done

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

  for i in ${!sites[@]};
  do
    site=${sites[$i]}
    echo "Site: " $site

    # Running Workflow, and get the timestamp and corruption log
    command="python3 ${WORKFLOW_BASE_DIR}/${NETWORK_WORKFLOW_ID}/workflow.py ${site} ${WORKFLOW_RESULT_DIR} run${run} ${JOB_NUMBER} -t ${WORKFLOW_RESULT_DIR}/run${run}_timestamps"
    echo ${command}
    ssh -n $SSH_OPTION ${WORKFLOW_USER}@${site}-submit ${command} > ${RESULT_DIR}/run${run}_${site}_console.out 2>&1
    scp $SSH_OPTION ${WORKFLOW_USER}@${site}-submit:${WORKFLOW_RESULT_DIR}/run${run}_timestamps ${RESULT_DIR}/run${run}_${site}_timestamps
  done

    # kill the cj network corrupter process and log the time
    if [ $param_I != "0" ]; then
      ${OUTPUT_DIR}/revert_previous.sh
      rm ${OUTPUT_DIR}/revert_previous.sh
      echo $(date +%s) CORRUPT_END "${link//_/.}" >> ${link_corrupt_log}
    fi
done < ${CORRUPT_EDGES_FILE}



if [ $run != 0 ]; then
  sleep 30
fi

# get elastic search csv file
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_end
echo "python3 /root/IRIS/es/iris-es-to-ml.py -s $(cat ${RESULT_DIR}/ts_start) -e $(cat ${RESULT_DIR}/ts_end)"
python3 /root/IRIS/es/iris-es-to-ml.py -s $(cat ${RESULT_DIR}/ts_start) -e $(cat ${RESULT_DIR}/ts_end)
mv transfer-events.csv ${RESULT_DIR}/transfer-events.csv
python3 iris_gen_result.py $RESULT_DIR

cp /root/run_wf_experiment.log ${RESULT_DIR}/
tar -czvf ${OUTPUT_DIR}/${RESULT_PREFIX}_${currenttime}.tar.gz $RESULT_DIR

echo "Data parsed and zipped: "
echo ${OUTPUT_DIR}/${RESULT_PREFIX}_${currenttime}.tar.gz
