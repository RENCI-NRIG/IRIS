#!/usr/bin/env python3

import getpass
import hashlib
import os

from Pegasus.api import *


def sha256(fname):
    with open(fname,"rb") as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

# used all over the place
username = getpass.getuser()
base_dir = os.getcwd()

wf = Workflow('bypass-staging-1-cache-corrupt')

# transformations
tc = TransformationCatalog()
script = Transformation('job.sh',
                        site='uc-staging',
                        pfn='http://uc-staging/~{}/inputs/job-wrapper.sh'.format(username),
                        is_stageable=True)
tc.add_transformations(script)

# a list of common inputs for all jobs
inputs = []
rc = ReplicaCatalog()
for entry in os.listdir('inputs/'):
    infile = File(entry)
    inputs.append(infile)
    chksum = sha256('inputs/{}'.format(entry))
    rc.add_replica('uc-staging',
                   infile,
                   'http://uc-staging/~{}/inputs/{}'.format(username, entry),
                    checksum_type='sha256',
                    checksum_value=chksum)

for i in range(100):
    j = Job(script)
    j.add_args(i)
    j.add_inputs(*inputs)
    wf.add_jobs(j)

wf.add_transformation_catalog(tc)
wf.add_replica_catalog(rc)
wf.write('workflow.yml')


