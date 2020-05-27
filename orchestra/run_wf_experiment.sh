#!/bin/bash
set -uex

source ./test_env.sh
source ./include.sh
_get_corrupt_nodes
_get_corrupt_edges
_get_end_nodes
export END_NODES=${END_NODES}
echo ${END_NODES_ARRAY[*]}
echo $end_nodes_count

currenttime=$(date +"%Y%m%d_%H%M%p")
RESULT_DIR=${OUTPUT_DIR}/output_${currenttime}
mkdir $RESULT_DIR
cp ${OUTPUT_DIR}/${NODE_ROUTER_FILE} ${RESULT_DIR}/${NODE_ROUTER_FILE}

run=$((START_RUN-1))
if [ $run == 0 ]
then
  if [ -f ${RESULT_DIR}/${RUN_LINKLABEL_FILE} ]; then
    rm ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
  fi
  touch ${RESULT_DIR}/${RUN_LINKLABEL_FILE}
fi

##### experiment starts ######
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_start

# corrupt storage in CORRUPT_NODES
echo $CORRUPT_NODES
for v_nodeip in $CORRUPT_NODES
do
  run=$((run+1))
  echo "### New Run" run${run}
  _get_hostname $v_nodeip
  v_node=$RETURN_HOSTNAME
  echo "Corrupting" $v_node

  # Running Workflow, and get the timestamp and corruption log
  ssh -n $SSH_OPTION ${WORKFLOW_USER}@uc-submit python3 /home/${WORKFLOW_USER}/IRIS/experiments/run.py ${currenttime} run${run} 01-bypass ${v_node}
  scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:/tmp/iris_corrupt.log ${RESULT_DIR}/${v_node}_run${run}_corrupt.log
  scp $SSH_OPTION ${WORKFLOW_USER}@uc-submit:/tmp/iris_timestamps ${RESULT_DIR}/run${run}_timestamps
done
cat ${CORRUPT_NODES_FILE} > ${RESULT_DIR}/$(basename ${RESULT_DIR}).txt

# corrupt network interface in CORRUPT_EDGES
#
# cat ${CORRUPT_EDGES_FILE} >> ${RESULT_DIR}/$(basename ${RESULT_DIR}).txt

# get elastic search csv file
echo $(date +%Y-%m-%dT%H:%M:%S) > ${RESULT_DIR}/ts_end
python3 /root/IRIS/es/iris-es-to-ml.py -s $(cat ${RESULT_DIR}/ts_start) -e $(cat ${RESULT_DIR}/ts_end)
mv transfer-events.csv ${RESULT_DIR}/transfer-events.csv
