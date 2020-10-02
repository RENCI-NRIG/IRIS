#!/usr/bin/python

import os
import re

def custom_grains():
    grains = {}
        
    grains['experiment'] = 'IRIS'

    grains['roles'] = []

    grains['roles'].append('common')

    # use hostname for now
    hostname = os.uname()[1]

    # http cache is site specific
    grains['site_http_proxy'] = re.sub(r'-.*', '-cache', hostname)

    if re.search('control', hostname, re.IGNORECASE):
        grains['roles'].append('control')
    elif re.search('submit', hostname, re.IGNORECASE):
        grains['roles'].append('submit')
    elif re.search('compute', hostname, re.IGNORECASE):
        grains['roles'].append('compute')
    elif re.search('staging', hostname, re.IGNORECASE):
        grains['roles'].append('staging')
    elif re.search('cache', hostname, re.IGNORECASE):
        grains['roles'].append('http_cache')

    return grains

