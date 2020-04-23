

/etc/apache2/conf-enabled/iris.conf:
  file:
    - managed
    - source: salt://apache2/iris.conf

apache2:
  pkg:
    - installed
  service.running:
    - enable: True
    - reload: True
    - watch:
      - file: /etc/apache2/conf-enabled/iris.conf





