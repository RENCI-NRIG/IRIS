
# allow https even when OCSP fails
/etc/apt/apt.conf.d/99verify-peer.conf:
  file:
    - managed
    - source: salt://apt/99verify-peer.conf

# Docker
docker-repo:
  pkgrepo.managed:
    - humanname: docker
    - name: deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable
    - file: /etc/apt/sources.list.d/docker.list
    - key_url: https://download.docker.com/linux/ubuntu/gpg

# HTCondor
htcondor-repo:
  pkgrepo.managed:
    - humanname: htcondor
    - name: deb http://research.cs.wisc.edu/htcondor/ubuntu/8.8/bionic bionic contrib
    - file: /etc/apt/sources.list.d/htcondor.list
    - key_url: https://research.cs.wisc.edu/htcondor/debian/HTCondor-Release.gpg.key

common_packages:
  pkg.installed:
    - pkgs:
      - vim

