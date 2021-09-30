# IRIS workflow experiment setup

### Add the experimenter’s username/key in the saltstack files on github:
saltstack/salt/users/init.sls
saltstack/salt/users/sudoers

### Use flukes to deploy https://github.com/RENCI-NRIG/IRIS/blob/master/exogeni-rdf/workflow-v3.rdf on exogeni.

### ssh into control node as root. 
(ssh  -i ~/.ssh/iris_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@129.7.98.66 -p 22)

### Make sure saltstack work is done. Note it might take hours to have all keys accepted.

```
root@control:~# salt-key -L
Accepted Keys:
cenic
control
esnet
internet2
starlight
syr-cache
syr-compute-c0
syr-compute-c1
syr-router-n2
syr-staging
syr-submit
uc-cache
uc-compute-c0
uc-compute-c1
uc-router-n0
uc-staging
uc-submit
ucsd-cache
ucsd-compute-c0
ucsd-compute-c1
ucsd-router-n3
ucsd-staging
ucsd-submit
unl-cache
unl-compute-c0
unl-compute-c1
unl-router-n1
unl-staging
unl-submit
Denied Keys:
Unaccepted Keys:
Rejected Keys:
```

### Follows description in https://github.com/RENCI-NRIG/IRIS/tree/master/orchestra/README.md
(without first step to clone, since postscript already does the clone for us)
And provide the following setting in the test_env.sh

```
export ES_USERNAME=<username for elasticsearch>
export ES_PASSWORD=<password for elasticsearch>
export WORKFLOW_USER=<your username>
```
