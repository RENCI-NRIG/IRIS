
condor:
  pkg:
    - installed
  service.running:
    - enable: True
    - reload: True
    - watch:
      - file: /etc/condor/config.d/10-base.conf
      - file: /etc/condor/pool_password

/etc/condor/pool_password:
  file:
    - managed
    - mode: 600
    - source: salt://local-conf/htcondor--pool_password

{% if 'submit' in salt['grains.get']('roles', []) %}

/etc/condor/config.d/10-base.conf:
  file:
    - managed
    - source: salt://htcondor/submit--10-base.conf

{% else %}

/etc/condor/config.d/10-base.conf:
  file:
    - managed
    - source: salt://htcondor/compute--10-base.conf

/usr/bin/user-job-wrapper:
  file:
    - managed
    - mode: 755
    - source: salt://htcondor/user-job-wrapper
    - template: jinja

{% endif %}

# we need 5.0.0dev
install_pegasus:
  pkg.installed:
    - sources:
      - pegasus: https://download.pegasus.isi.edu/pegasus/5.0.0dev/pegasus_5.0.0~dev-1+ubuntu18_amd64.deb
