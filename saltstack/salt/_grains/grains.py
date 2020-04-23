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
    if re.search('control', hostname, re.IGNORECASE):
        grains['roles'].append('control')
    elif re.search('submit', hostname, re.IGNORECASE):
        grains['roles'].append('submit')
    elif re.search('staging', hostname, re.IGNORECASE):
        grains['roles'].append('staging')
    elif re.search('compute', hostname, re.IGNORECASE):
        grains['roles'].append('compute')
        # all computes are http_caches for now
        grains['roles'].append('http_cache')
        grains['site_http_proxy'] = hostname

    return grains

