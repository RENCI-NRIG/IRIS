#!/bin/bash

# this script should be run as a post install on the ExoGENI nodes. Example:
# curl https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/bootstrap.sh | bash

umask 022

# this part should only run on the control node
if (echo $HOSTNAME | grep control) >/dev/null 2>&1; then

    rm -rf /srv/IRIS /srv/salt
    git clone https://github.com/RENCI-NRIG/IRIS.git /srv/IRIS
    ln -s /srv/IRIS/saltstack/salt /srv/salt

    apt install -y salt-master salt-minion
    systemctl enable salt-master
    systemctl restart salt-master

    # HTCondor pool password
    mkdir -p /srv/salt/local-conf
    uuidgen >/srv/salt/local-conf/htcondor--pool_password
fi

# the rest on all nodes
apt install -y salt-minion
echo 'master: control' >/etc/salt/minion.d/50-main.conf
perl -p -i -e 's;#default_include.*;default_include: minion.d/*.conf;' /etc/salt/minion
salt-call --state-verbose=false state.highstate
systemctl enable salt-minion
systemctl restart salt-minion

# also install a cron job to keep salt highstate
curl -o /etc/cron.d/salt https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/salt/salt/salt.cron
chmod 644 /etc/cron.d/salt
touch /etc/cron.d/salt
curl -o /usr/sbin/salt-highstate-cron https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/salt/salt/salt-highstate-cron
chmod 755 /usr/sbin/salt-highstate-cron

