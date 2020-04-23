
Each post setup script on the nodes in the ExoGENI deployment should
execute:

    curl https://raw.githubusercontent.com/RENCI-NRIG/IRIS/master/saltstack/bootstrap.sh | bash

After the nodes have been all come up, log in as root on `control` and
see if all nodes have checked in by running `salt-key -L`:

    root@control:~# salt-key -L
    Accepted Keys:
    Denied Keys:
    Unaccepted Keys:
    control
    uc-submit
    ...

If **all** the nodes under *Unaccepted Keys* are part of the experiment,
accept them all:

    root@control:~# salt-key -A
    
After one cup of coffee (~10 minutes), the nodes should be setup and ready
for commands. Test that they are all responding by issuing:

    root@control:~# salt '*' test.ping


