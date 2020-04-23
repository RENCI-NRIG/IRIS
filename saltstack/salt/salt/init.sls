
/etc/cron.d/salt:
  file.managed:
    - source: salt://salt/salt.cron
    - mode: 644

/usr/sbin/salt-highstate-cron:
  file.managed:
    - source: salt://salt/salt-highstate-cron
    - mode: 755

salt-minion:
  service.running:
    - enable: True
    - reload: True

