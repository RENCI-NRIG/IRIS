
/etc/sudoers:
  file:
    - managed
    - mode: 444
    - source: salt://users/sudoers


#### ericafu ####

ericafu:
  user.present:
    - fullname: Erica Fu
    - shell: /bin/bash
    - home: /home/ericafu
    - uid: 1002
    - groups:
      - users
  ssh_auth.present:
    - user: ericafu
    - names:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDebcxJiArFzZCWDwTMbH9xRaCQ/1c3e2MpKbTtTvRxX6QSvw6AqwZ3/2dOmHkJDmCSWEMVzwSwjvWmjfsCNz/PnA9hC76C4IGoQ644TErURBYDaRP7FbZpVKCB+nfTNUovOK0AUPJwmi33IaAR4aqrXBk+zXAZRVH0xDjZtNMN+7t24Nz1mdiigSWGzLz2ymyQYmQ9zVbdUewxnyamJIyXP3lByJsnQYdFmnJ0wgou7yVDrQgWCRRk8ISXIrRdP1H9KsaXWPCKYNTS8/k4FbMMybaPn1KjBJ+QxNWgZCGJx6fpOnArECBEMMFLUl+xonLOZDnq+Cf/gwUrg+yGjI5f ericafu
  
ericafu-internal:
  ssh_auth.present:
    - user: ericafu
    - source: salt://local-conf/ssh.ericafu.pub

/home/ericafu/.ssh/config:
  file:
    - managed
    - source: salt://users/ssh.config
    - user: ericafu
    - group: users
    - mode: 644

/home/ericafu/.ssh/id_rsa:
  file:
    - managed
    - source: salt://local-conf/ssh.ericafu
    - user: ericafu
    - group: users
    - mode: 600

/home/ericafu/.ssh/id_rsa.pub:
  file:
    - managed
    - source: salt://local-conf/ssh.ericafu.pub
    - user: ericafu
    - group: users
    - mode: 644

#### rynge ####

rynge:
  user.present:
    - fullname: Mats Rynge
    - shell: /bin/bash
    - home: /home/rynge
    - uid: 1004
    - groups:
      - users
  ssh_auth.present:
    - user: rynge
    - names:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC3e1TSFh19+nWBOoSmOnbzgjsYhxdM4ONfuDCJQubkt/WLOstkzCLGozCAKQ4SubkBWbwBi70gfGA2K9am8wnXX+//77LuJUN2mQWOKnGo0mwhnygRIWfFEZaEGwsBa0pDXxty5J9SDX3YGEcFWUSJefSQhnpzt76jj+0M4k2sgOuydHi6hKoHDyb0qkRujlUnqnenbxz3pnyzncFqL5yyu8F1YtHEMQz86B0UPGqmdYwS6dK1uUPgrI6D3MmOfJoVyhefJoCLRDiNi6jKWTwQskAPHHLw0vyo+UGDzA6knCPdpd9jWWR3REX5Mj39d5nKj/Fo9YU9F01I2R8uZorTfCTnHhN/32puvnjjJp+BvpbR+nB4ir2umxl6DLPp7ZhdV782KdpGfTMKmYAreGKiAbAWg5hqHrPTdZFS1of7pJMV/Fx45+Zpa1XeP8VaaVd4dmbK1jsFQHNNYjyjy8u2fbOsEbbC6hARryoO0DVak5BwEqZZIkWhgh3fb5CKGrDLPBAKI5qphBPT0206urE4zOU+XqSFyuICPAAlS8XtBBtIENN3N4n5WX6wiK58prx9uSyJx+1cdUtr9uw65c26UXtfO8a5VcKvlMPFMCoBdCNZxYsf1J2aH5/MOA5DyH0f/3qlusMoA0vQ8hQp7U5FfVXTO2c9ApXctF78TJ+eTQ== rynge@fenrir

rynge-internal:
  ssh_auth.present:
    - user: rynge
    - source: salt://local-conf/ssh.rynge.pub

/home/rynge/.ssh/config:
  file:
    - managed
    - source: salt://users/ssh.config
    - user: rynge
    - group: users
    - mode: 644

/home/rynge/.ssh/id_rsa:
  file:
    - managed
    - source: salt://local-conf/ssh.rynge
    - user: rynge
    - group: users
    - mode: 600

/home/rynge/.ssh/id_rsa.pub:
  file:
    - managed
    - source: salt://local-conf/ssh.rynge.pub
    - user: rynge
    - group: users
    - mode: 644

#### tanaka ####

tanaka:
  user.present:
    - fullname: Ryan Tanaka
    - shell: /bin/bash
    - home: /home/tanaka
    - uid: 1005
    - groups:
      - users
  ssh_auth.present:
    - user: tanaka
    - names:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC+lkUPDYqwUAFB05PA4bViVpN+xSsWgVdhXjbJapPyqWXW22GOtPpC5S+jtLil1e2etL0Qs8WbggjtFRN06uDZ/8VPVSpwn1L8AO8GN1wYwIQdpqEMYVN2Fc6OKJ0dmTAPLsZKNvmNPLECken7Mvpc0DDNFoBfV9gB3fDteNlY5VwANymCiNkrKI1WKHyYNGmQmLSMqQ1jwNg8W5ylMruufSqKG74iW82IPyV2EWA7sweLcNYktswR7ecYqfG+AWXR5gyhCXCgiQLuCDJqZq4zYzXg3421x2SbjsFN42gLYCuh1uBEiC9zhg6rIdOMif86fJAwKhYXctZ9rr+mrd9TGJ+0Wg4pOklQGAPedDS4dFR3+melr2GCYnVTEt3wtFwRISxdMZInN/tFPbhzpI810h9A9DuSU++fOJWJt7iX7YIm1pnvPJSSUpPxPUcuWltR0CUhDcZUW5zLMcJteTH9pKmKe2EW8qL0+QyEifiMW3R7yaxbI/hDZafrRXZJW+zPpqkYYoDFMPduKwz3khoMdFaW2Y2XT+8r3Ny1q/ll2YL6UyRXJ4DoVOV72CRek0drl8NBcIi31YyI2USZxxY0wigRIt4dwup9tbt9CSxfBLpDlfGUFB5G5ATCzGpHuAJkZ+V+4vOiZbLvHegls/K24gh6npqebLAn+AnXu9alaQ== tanaka@isi.edu

tanaka-internal:
  ssh_auth.present:
    - user: tanaka
    - source: salt://local-conf/ssh.tanaka.pub

/home/tanaka/.ssh/config:
  file:
    - managed
    - source: salt://users/ssh.config
    - user: tanaka
    - group: users
    - mode: 644

/home/tanaka/.ssh/id_rsa:
  file:
    - managed
    - source: salt://local-conf/ssh.tanaka
    - user: tanaka
    - group: users
    - mode: 600

/home/tanaka/.ssh/id_rsa.pub:
  file:
    - managed
    - source: salt://local-conf/ssh.tanaka.pub
    - user: tanaka
    - group: users
    - mode: 644

#### vahi ####

vahi:
  user.present:
    - fullname: Karan vahi
    - shell: /bin/bash
    - home: /home/vahi
    - uid: 1006
    - groups:
      - users
  ssh_auth.present:
    - user: vahi
    - names:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDD4iUwbgndUivz8ccR8/Lx/pe+i54xvOHXxn8Qmni+8Ga7tBqFE58ZCQiMCfOxXT+Q9pMZbK+FCSqgSz37gEuY2jb43Tu6+5gab3LCgIgyr25NAGQeaV5fWseifI4z2HqllG/gBJSHH9qHglgXOQ2Jgx4eus9ENrChBHulccFHA1YSYqJRCzDY4//dsfx3aYSwFJeLnN/wXuI7j/NJmKTgGRc9pQzBYxB0GD+vlnhQZes84ud5B5vO0xgL6idyjcL+G/phbcuev/fzbZuFobTh8dIQ+7VOgHqWB0KAdEOQGKDEx+Op80/X7sNLlLg+Ne3GSUdw8wUT2n3faggfEGQt 2016 RSA key

vahi-internal:
  ssh_auth.present:
    - user: vahi
    - source: salt://local-conf/ssh.vahi.pub

/home/vahi/.ssh/config:
  file:
    - managed
    - source: salt://users/ssh.config
    - user: vahi
    - group: users
    - mode: 644

/home/vahi/.ssh/id_rsa:
  file:
    - managed
    - source: salt://local-conf/ssh.vahi
    - user: vahi
    - group: users
    - mode: 600

/home/vahi/.ssh/id_rsa.pub:
  file:
    - managed
    - source: salt://local-conf/ssh.vahi.pub
    - user: vahi
    - group: users
    - mode: 644



