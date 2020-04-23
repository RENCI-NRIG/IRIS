
/etc/cron.d/salt:
  file.managed:
    - source: salt://salt/salt.cron
    - mode: 644



/usr/sbin/salt-highstate-cron:
  file.managed:
    - source: salt://salt/salt-highstate-cron
    - mode: 755

