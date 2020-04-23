
docker-ce:
  pkg:
    - installed
  service.running:
    - name: docker
    - enable: True

/cache:
  file.directory:
    - user: root
    - group: root
    - mode: 755

iris-http-proxy.systemd-unit:
  file.managed:
    - name: /etc/systemd/system/iris-http-proxy.service
    - source: salt://http-cache/iris-http-proxy.service

  module.run:
    - name: service.systemctl_reload
    - onchanges:
      - file: iris-http-proxy.systemd-unit

iris-http-proxy:
  service.running:
    - name: iris-http-proxy
    - reload: False
    - watch:
      - module: iris-http-proxy.systemd-unit

