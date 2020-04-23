base:
  '*':
    - salt

  'roles:common':
    - match: grain
    - apt
    - users

  'roles:submit':
    - match: grain
    - htcondor
  
  'roles:compute':
    - match: grain
    - htcondor

  'roles:staging':
    - match: grain
    - apache2

  'roles:http_cache':
    - match: grain
    - http-cache

