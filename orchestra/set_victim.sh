#!/bin/bash
set -ue

source "${BASH_SOURCE%/*}/test_env.sh"

rm $CORRUPT_NODES_FILE
rm $CORRUPT_EDGES_FILE
touch $CORRUPT_NODES_FILE
touch $CORRUPT_EDGES_FILE

echo "victim is set: "
if [[ $1 == *"Link"* ]]; then
    victim=$(cat ${CORRUPT_EDGES_FILE}.all | grep $1 )
    echo $victim > $CORRUPT_EDGES_FILE
    echo $(cat $CORRUPT_EDGES_FILE)
else
    victim=$(cat ${CORRUPT_NODES_FILE}.all | grep $1 )
        echo $victim > $CORRUPT_NODES_FILE
        echo $(cat $CORRUPT_NODES_FILE)
fi

