

{% if 'control' in salt['grains.get']('roles', []) %}

/etc/cron.d/salt:
  file.managed:
    - source: salt://salt/salt.cron.control
    - mode: 644

{% else %}

/etc/cron.d/salt:
  file.managed:
    - source: salt://salt/salt.cron
    - mode: 644

{% endif %}

/usr/sbin/salt-highstate-cron:
  file.managed:
    - source: salt://salt/salt-highstate-cron
    - mode: 755

/usr/sbin/salt-update-ssh-keys:
  file.managed:
    - source: salt://salt/salt-update-ssh-keys
    - mode: 755

salt-minion:
  service.running:
    - enable: True
    - reload: True

