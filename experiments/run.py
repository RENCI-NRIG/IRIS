#!/usr/bin/env python
import os
import subprocess

from datetime import datetime
from pathlib import Path

'''
Setup experiment directory. 

$HOME/workflow-batch-experiment-runs
├── 1588029671             <-- time at which batch run initiated
│   ├── 01-test-workflow   <-- executed workflow directory
│   └── 02-bypass-staging-1-cache-corrupt 
└── 1588030368   
    ├── 01-test-workflow 
    └── 02-bypass-staging-1-cache-corrupt
'''
EXPERIMENT_DIR = Path(os.getenv("HOME")) / "worklow-batch-experiment-runs"

try:
    Path.mkdir(EXPERIMENT_DIR)
except FileExistsError:
    pass

BATCH_RUN_DIR =  EXPERIMENT_DIR / Path(datetime.now().strftime("%s"))
Path.mkdir(BATCH_RUN_DIR)

# child processes will run from this dir when run as batch experiments
os.environ["EXPERIMENT_WORK_DIR"] = str(BATCH_RUN_DIR)

# --- Run each workflow sequentially -------------------------------------------
workflow_dir = Path("workflows")
workflows = [wf for wf in workflow_dir.iterdir() if wf.is_dir()]

# always run in order 00, 01, ... 0N
workflows.sort(key=lambda p: str(p))
for wf in workflows:
    # leaving this to the wf script so each wf is self contained
    # kick off iris-experiment-driver asynchronously
    #iris_experiment_driver = subprocess.Popen([wf + "/iris-experiment-driver"])

    # blocking call to run wf
    subprocess.run(["python3", wf + "/workflow.py"])

    # wf complete, kill iris-experiment-driver
    #iris_experiment_driver.terminate()

