#!/usr/bin/env python
import os
import sys

from Pegasus.api import *

def write_basic_site_catalog(path: str, work_dir: str, run_id: str) -> None:
    # create local site
    SSH_PRIVATE_KEY_PATH = os.getenv("HOME") + "/.ssh/id_rsa"
    LOCAL_SHARED_SCRATCH_PATH = work_dir + "/" + run_id
    LOCAL_LOCAL_STORAGE_PATH = work_dir + "/outputs/" + run_id

    local = Site("local", arch=Arch.X86_64, os_type=OS.LINUX)\
                .add_directories(
                    Directory(Directory.SHAREDSCRATCH, LOCAL_SHARED_SCRATCH_PATH)
                        .add_file_servers(FileServer("file://" + LOCAL_SHARED_SCRATCH_PATH, Operation.ALL)),
                    
                    Directory(Directory.LOCALSTORAGE, LOCAL_LOCAL_STORAGE_PATH)
                        .add_file_servers(FileServer("file://" + LOCAL_LOCAL_STORAGE_PATH, Operation.ALL))
                )\
                .add_profiles(Namespace.PEGASUS, SSH_PRIVATE_KEY=SSH_PRIVATE_KEY_PATH)\
                .add_env(LANG="C.UTF-8")

    # create origin (staging) site
    ORIGIN_SHARED_SCRATCH_PATH = os.getenv("HOME") + "/public_html/"
    ORIGIN_FILE_SERVER_GET_URL = "http://uc-staging/~" + os.getenv("USER") + "/"
    ORIGIN_FILE_SERVER_PUT_URL = "scp://" + os.getenv("USER") + "@uc-staging/home/" + os.getenv("USER") + "/public_html"
    
    origin = Site("origin", arch=Arch.X86_64, os_type=OS.LINUX)\
                .add_directories(
                    Directory(Directory.SHAREDSCRATCH, ORIGIN_SHARED_SCRATCH_PATH)
                        .add_file_servers(
                            FileServer(ORIGIN_FILE_SERVER_GET_URL, Operation.GET),
                            FileServer(ORIGIN_FILE_SERVER_PUT_URL, Operation.PUT)
                        )
                )\
                .add_env(LANG="C.UTF-8")
    
    # create condorpool site 
    condorpool = Site("condorpool", arch=Arch.X86_64, os_type=OS.LINUX)\
                    .add_pegasus_profile(style="condor")\
                    .add_condor_profile(universe="vanilla")\
                    .add_env(LANG="C.UTF-8")

    
    # write catalog to path 
    sc = SiteCatalog()\
            .add_sites(local, origin, condorpool)\
            .write(path)
