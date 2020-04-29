#!/usr/bin/env python

from Pegasus.api import *

def write_basic_properties(path: str) -> None:
    props = Properties()
    props["pegasus.data.configuration"] = "nonsharedfs"
    props["pegasus.monitord.encoding"] = "json"
    props["pegasus.catalog.workflow.amqp.url"] = "amqp://friend:donatedata@msgs.pegasus.isi.edu:5672/prod/workflows"
    props["dagman.retry"] = "2"
    props.write(path)
    
