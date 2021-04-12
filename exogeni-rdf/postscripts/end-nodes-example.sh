#!/bin/bash

#set ( $linkset = $self.Links()  )
#set ( $linksetstr = $self.AllLinks()  )
#set ( $num = $linkset.size() )
#set ( $numIntf = $num + 2 )
echo $linkset >> /root/tmp
echo $linksetstr >> /root/tmp

#set ( $link = $linkset[0] )
echo $link > /root/tmp
#set ( $gw = $ucsd-router-n3.IP($link) )
echo $gw > /root/tmp

while ! ping -c 1 -n -w 1 $gw &> /dev/null
do
    echo "ping gw...." >> /root/tmp
    sleep 2
done
echo "\n%s\n"  "Server is back online" >> /root/tmp

ip route add 10.100.0.0/16 via $gw dev ens6
ip route add 172.16.0.0/16 via $gw dev ens6
ip route add 192.168.0.0/16 via $gw dev ens6


echo "following are for chaos-jungle and saltstack" >> /root/tmp

#set ( $hostname = $self.Name() )
echo $hostname:$gw > /root/tmp_gw
#foreach ( $link2 in $linkset )
  #set ( $IP=$self.IP($link2) )
  echo export $self.Name()_$link2="$IP" >> /root/tmp_links.sh
#end

echo "Installing CJ and apache2" >> /root/tmp
cd /root
git clone --branch storage https://github.com/RENCI-NRIG/chaos-jungle.git
git clone https://github.com/RENCI-NRIG/IRIS.git
date >> /root/tmp
until apt-get -y install apache2
do
        echo "installing apache2" >> /root/tmp
        sleep 2
done
date >> /root/tmp
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4052245BD4284CDD
echo "deb https://repo.iovisor.org/apt/$(lsb_release -cs) $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/iovisor.list
apt-get -y update
apt-get -y install bcc-tools libbcc-examples linux-headers-$(uname -r)
apt-get -y install python3-bcc
apt-get -y install python3-pyroute2 python-pyroute2 iperf3
apt install -y python3-pip python3-setuptools
pip3 install python-crontab
date >> /root/tmp
python3 /root/chaos-jungle/storage/cj_storage.py --revert >> /root/tmp
echo "start saltstack" >> /root/tmp
curl https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/bootstrap.sh | bash
echo "done" >> /root/tmp
