#!/bin/bash

echo ! > /root/tmp
#wait for Internet
while ! ping -c1 127.0.0.53 &>/dev/null
        do echo "Ping Fail" >> /root/tmp
        sleep 2
done
echo "Internet is ready" >> /root/tmp

#Install Quagaa
until apt-get update -y
do
        echo "updating Ubunut...." >> /root/tmp
        sleep 2
done
until apt-get install -y quagga
do
        echo "installing quagga...." >> /root/tmp
        sleep 2
done

echo 'VTYSH_PAGER=more' >>/etc/environment
echo 'export VTYSH_PAGER=more' >>/etc/bash.bashrc

#cp /usr/share/doc/quagga/examples/zebra.conf.sample /etc/quagga/zebra.conf
#cp /usr/share/doc/quagga/examples/ospfd.conf.sample /etc/quagga/ospfd.conf

#set ( $linkset = $self.Links()  )
#set ( $linksetstr = $self.AllLinks()  )
#set ( $num = $linkset.size() )
#set ( $numIntf = $num + 2 )

echo $linkset >> /root/tmp
echo $linksetstr >> /root/tmp

#wait for interfaces
echo $numIntf >> /root/tmp
size=0
while [ $size -lt $numIntf ]
do
filelist=( $(ls /etc/udev/rules.d) )
size="${#filelist[@]}"
done
echo $size $numIntf >> /root/tmp

#ospfd.conf
echo ! >> /etc/quagga/ospfd.conf
#foreach ( $ospfLink in $linkset )
#set ( $mac = $self.MAC( $ospfLink ) )
for file in /etc/udev/rules.d/*
do
if grep -q $mac $file
then
echo $file >> /root/tmp
ospfIntf=$(cat $file | sed -n -e 's/^\(.*\)\(ens[0-9]*\)\(.*\)/\2/p' )
echo $ospfIntf >> /root/tmp
echo interface $ospfIntf >> /etc/quagga/ospfd.conf
fi
done
#end

echo router ospf >> /etc/quagga/ospfd.conf
#foreach ( $link in $linkset )
  #set ( $IP=$self.IP($link) )
  #set ( $MASK=$self.Netmask($link) )
  IFS=. read -r i1 i2 i3 i4 <<< $IP
  #if ( $MASK == "/24" )
    SUBNET="$i1.$i2.$i3.0"
  #end
  #if ( $MASK == "/16" )
    SUBNET="$i1.$i2.0.0"
  #end
  echo  network $SUBNET$MASK area 0 >> /etc/quagga/ospfd.conf
#end
echo line vty >> /etc/quagga/ospfd.conf

#zebra.conf

echo ! > /etc/quagga/zebra.conf

#foreach ( $zebralink in $linkset )
#set ( $IP=$self.IP( $zebralink ) )
#set ( $MASK=$self.Netmask( $zebralink ) )
#set ( $mac = $self.MAC( $zebralink ) )
echo $IP$MASK $mac  >> /root/tmp
for file in /etc/udev/rules.d/*
do
if grep -q $mac $file
then
echo $file >> /root/tmp
intf=$(cat $file | sed -n -e 's/^\(.*\)\(ens[0-9]*\)\(.*\)/\2/p' )
echo $intf >> /root/tmp
echo interface $intf >> /etc/quagga/zebra.conf
fi
done
echo ip address $IP$MASK >> /etc/quagga/zebra.conf
#end
echo ip forwarding >> /etc/quagga/zebra.conf

#start zebra and ospfd

systemctl enable zebra
systemctl start zebra
systemctl enable ospfd
systemctl start ospfd

#foreach ( $link2 in $linkset )
  #set ( $IP=$self.IP($link2) )
  echo export $self.Name()_$link2="$IP" >> /root/tmp_links.sh
#end

echo "Installing CJ and apache2" >> /root/tmp
cd /root
git clone --branch storage https://github.com/RENCI-NRIG/chaos-jungle.git
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


