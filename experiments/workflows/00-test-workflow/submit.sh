#!/bin/bash

set -e

TOP_DIR=`pwd`

export WORK_DIR=$HOME/workflows
mkdir -p $WORK_DIR

export RUN_ID=test-workflow-`date +'%s'`

# SET THESE VARIABLES
SSH_PRIVATE_KEY_PATH=$HOME/.ssh/id_rsa
ORIGIN_SHARED_SCRATCH_PATH=$HOME/public_html/

# FILL IN <ip>
ORIGIN_FILE_SERVER_GET_URL=http://uc-staging/~$USER/  
ORIGIN_FILE_SERVER_PUT_URL=scp://$USER@uc-staging/home/$USER/public_html

cat > sites.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<sitecatalog xmlns="http://pegasus.isi.edu/schema/sitecatalog" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://pegasus.isi.edu/schema/sitecatalog http://pegasus.isi.edu/schema/sc-4.0.xsd" version="4.0">
    <!-- local -->
    <site  handle="local" arch="x86_64">
        <profile namespace="pegasus" key="SSH_PRIVATE_KEY" >$SSH_PRIVATE_KEY_PATH</profile>

        <directory type="shared-scratch" path="$WORK_DIR/$RUN_ID">
            <file-server operation="all" url="file://$WORK_DIR/$RUN_ID"/>
        </directory>
        <directory type="local-storage" path="$WORK_DIR/outputs/$RUN_ID">
            <file-server operation="all" url="file://$WORK_DIR/outputs/$RUN_ID"/>
        </directory>
    </site>

    <!-- staging -->
    <site handle="origin" arch="x86_64" os="LINUX">
        <directory type="shared-scratch" path="$ORIGIN_SHARED_SCRATCH_PATH">
            <file-server operation="get" url="$ORIGIN_FILE_SERVER_GET_URL"/>
            <file-server operation="put" url="$ORIGIN_FILE_SERVER_PUT_URL"/>
        </directory>
    </site>

    <!-- execution -->
    <site  handle="condorpool" arch="x86_64" os="LINUX">
        <profile namespace="pegasus" key="style" >condor</profile>
        <profile namespace="condor" key="universe" >vanilla</profile>
    </site>
</sitecatalog>
EOF

# generate the workflow
PYTHONPATH=`pegasus-config --python`
export PYTHONPATH=".:$PYTHONPATH"
./workflow_gen.py

# pegasus properties 
cat > pegasus.conf << EOF
pegasus.data.configuration = nonsharedfs
pegasus.monitord.encoding = json
pegasus.catalog.workflow.amqp.url = amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows
dagman.retry = 0
pegasus.transfer.arguments = -m 1
EOF

# plan
pegasus-plan \
    --conf pegasus.conf \
    --force \
    --dir $WORK_DIR \
    --relative-dir $RUN_ID \
    --sites condorpool \
    --staging-site condorpool=origin \
    --output-site local \
    --dax workflow.xml \
    --cluster horizontal

# run
pegasus-run $WORK_DIR/$RUN_ID

