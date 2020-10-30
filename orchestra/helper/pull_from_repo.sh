#!/bin/bash

source ./test_env.sh
source ./include.sh
set -u
sites=("uc" "syr" "ucsd" "unl")
n_sites=${#sites[@]}

echo for ${WORKFLOW_USER}@control:

sudo -u $WORKFLOW_USER bash -c "cd /home/${WORKFLOW_USER}/IRIS; git pull"
for (( i=0; i<$n_sites; i++ ));
  do
    site=${sites[$i]}; echo "for site ${site}:"
    ${SSH_CMD} ${site}-submit "cd IRIS; git pull"
done
