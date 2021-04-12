#!/bin/bash

cd /root
git clone -b storage https://github.com/RENCI-NRIG/chaos-jungle.git
git clone https://github.com/RENCI-NRIG/IRIS.git

wget -O - https://repo.saltstack.com/py3/ubuntu/18.04/amd64/latest/SALTSTACK-GPG-KEY.pub | sudo apt-key add -
echo "deb http://repo.saltstack.com/py3/ubuntu/18.04/amd64/latest bionic main" > /etc/apt/sources.list.d/saltstack.list
apt-get -y update

until apt-get -y install salt-master
do
        echo "installing salt-master" >> /root/tmp
        sleep 5s
done

echo "start saltstack" >> /root/tmp
curl https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/bootstrap.sh | bash

while !(salt-key -L | grep syr-router-n2) || !(salt-key -L | grep unl-router-n1) || !(salt-key -L | grep ucsd-router-n3) || !(salt-key -L | grep uc-router-n0) || !(salt-key -L | grep syr-compute-c1) || !(salt-key -L | grep syr-compute-c0) || !(salt-key -L | grep unl-compute-c1) || !(salt-key -L | grep unl-compute-c0) || !(salt-key -L | grep ucsd-compute-c1) || !(salt-key -L | grep ucsd-compute-c0) || !(salt-key -L | grep uc-compute-c0) || !(salt-key -L | grep uc-compute-c1) || !(salt-key -L | grep uc-staging) || !(salt-key -L | grep uc-submit) || !(salt-key -L | grep syr-staging) || !(salt-key -L | grep syr-submit) || !(salt-key -L | grep ucsd-staging) || !(salt-key -L | grep ucsd-submit) || !(salt-key -L | grep unl-staging) || !(salt-key -L | grep unl-submit) || !(salt-key -L | grep unl-cache) || !(salt-key -L | grep uc-cache) || !(salt-key -L | grep syr-cache) || !(salt-key -L | grep ucsd-cache)
do
sleep 5s
echo "saltstack not ready, sleep 5s" >> /root/tmp
done

sleep 1m
salt-key -L >> /root/tmp
salt-key -y -A >> /root/tmp
echo "done" >> /root/tmp
