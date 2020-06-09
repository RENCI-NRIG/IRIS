#!/usr/bin/env python3
import logging
import os
import subprocess
import sys

from datetime import datetime
from pathlib import Path
from shutil import copyfile

log = logging.getLogger(__file__)


def print_green(a, **kwargs): print("\033[92m{}\033[00m".format(a), **kwargs)
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
EXPERIMENT_DIR = Path(os.getenv("HOME")) / "workflow-batch-experiment-runs"
fh = logging.FileHandler(str(EXPERIMENT_DIR / "experiment.log"))
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
log.addHandler(fh)

try:
    Path.mkdir(EXPERIMENT_DIR)
except FileExistsError:
    pass

log.info("Experiment directory set: {}".format(str(EXPERIMENT_DIR)))
BATCH_RUN_DIR = EXPERIMENT_DIR / Path(datetime.now().strftime("%s"))

# Expected argv:
# sys.argv[1]: testname
# sys.argv[2]: run id
# sys.argv[3]: workflow name
# sys.argv[4]: corrupt site

corrupt_site = None
timestamps_file = None
workflow = None
if len(sys.argv) > 3:
    testname = sys.argv[1]
    runid = sys.argv[2]
    workflow = sys.argv[3]
    BATCH_RUN_DIR = EXPERIMENT_DIR / Path(testname + "-" + runid + "-" + datetime.now().strftime("%s"))
    timestamps_file = str(BATCH_RUN_DIR) + '/' + runid + '_timestamps'

if len(sys.argv) > 4:
    corrupt_site = sys.argv[4]

if len(sys.argv) > 3:
    log.info("test name: {}, run id: {}, workflow: {}, batch run dir: {}, timestamps file: {}, corrupt site: {}".format(
        testname,
        runid,
        workflow,
        BATCH_RUN_DIR,
        timestamps_file,
        corrupt_site
    ))

print(BATCH_RUN_DIR)
Path.mkdir(BATCH_RUN_DIR)

# child processes will run from this dir when run as batch experiments
os.environ["EXPERIMENT_WORK_DIR"] = str(BATCH_RUN_DIR)

# --- Run each workflow sequentially -------------------------------------------
workflow_dir = Path(__file__).parent.absolute() / Path("workflows")
workflows = [wf for wf in workflow_dir.iterdir() if wf.is_dir()]


print_green("Initiating Experiment Run at: {}".format(BATCH_RUN_DIR.resolve()))

# always run in order 00, 01, ... 0N
workflows.sort(key=lambda p: str(p))
for wf in workflows:
    print_green("Running Workflow: {}".format(wf.name))
    if workflow and (workflow not in str(wf)):
        continue

    if timestamps_file:
        with open(timestamps_file, 'w') as f:
            f.write(datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " START")

    # leaving this to the wf script so each wf is self contained
    # kick off iris-experiment-driver asynchronously
    #iris_experiment_driver = subprocess.Popen([wf + "/iris-experiment-driver"])

    # blocking call to run wf
    if corrupt_site:
        print_green("[Run {}]: Running Workflow: {} and corrupt {}".format(runid, wf.name, corrupt_site))
        wf_run = subprocess.run(["python3", str(wf.resolve() / "workflow.py"), corrupt_site, runid], cwd=wf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        wf_run = subprocess.run(["python3", str(wf.resolve() / "workflow.py")], cwd=wf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if wf_run.returncode != 0:
        log.critical(wf_run.stdout.decode() + "\n" + wf_run.stderr.decode())
        sys.exit(1)

    # wf complete, kill iris-experiment-driver
    #iris_experiment_driver.terminate()

    if timestamps_file:
        with open(timestamps_file, 'a') as f:
            f.write('\n' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + " END")
        copyfile(timestamps_file, '/tmp/iris_timestamps')  # so control machine can grap it easily
