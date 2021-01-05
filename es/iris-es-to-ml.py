#!/usr/bin/env python3
import csv

import time
import datetime
from calendar import timegm
import os
import sys
import re
import optparse
import csv

from dateutil.parser import parse
from pprint import pprint, pformat

from elasticsearch import helpers
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q


def get_events(client, start_dt):
    '''
    Return a set of events matching the criterias
    '''
     
    start_time = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
    end_dt = start_dt + datetime.timedelta(hours = 1)
    end_time = end_dt.strftime('%Y-%m-%dT%H:%M:%S')
    print('Quering for data in ' + start_time + ' .. ' + end_time)

    q = Q('bool', must=[
            Q('match', event='stampede.job_inst.composite'),
            Q('match_phrase', pegasus_version='5.0.0dev'),
            Q('match', submit_hostname='uc-submit'),
            Q('exists', field='transfer_attempts')
        ])

    s = Search(using=client, index='pegasus-composite-events-*') \
               .query(q) \
               .filter('range', ** {'@timestamp': {'gt': start_time, 'lt':end_time, 'time_zone': '+00:00'}}) 

    s = s.sort('ts')  
    s = s[0:10000]

    try:
        response = s.execute()
        if not response.success():
            raise
    except Exception as e:
        print(e, 'Error accessing Elasticsearch')
        sys.exit(1)
 
    data = []
    for entry in response.to_dict()['hits']['hits']:
        data.append(entry['_source'])
            
    return data


def find_integrity_data(lfn, intgrity_data):
    '''
    Walk thew integrity_data list and find a matching entry
    '''
    for check in intgrity_data:
        if check['lfn'] == lfn:
            if 'sha256_expected' not in check:
                check['sha256_expected'] = None
            return check
    return {'success': None,
            'sha256': None,
            'sha256_expected': None}


def proto_host(s):
    m = re.search('^\w+://[\w\.-]*', s)
    if m:
        return m.group()
    if s[0] == '/':
        return 'file://'
    return ''


def safe_member(d, key):
    if key not in d:
        return ''
    return d[key]


def extract_site(host):
    '''
    given a hostname, try to come up with a normalized site label
    '''
    
    site = host
    comp = host.split('.')
    
    if len(comp) > 1:
        # full hostname, strip tld and use only the domain
        site = comp[-2]

    # if we are on the exogeni testbed, we can drop part
    # of the hostname
    if host.startswith('syr-') or \
       host.startswith('unl-') or \
       host.startswith('uc-') or \
       host.startswith('ucsd-'):
        site = re.sub(r'-.*', '', site)

    return site


def fix_label(t, endp):
    '''
    replaces the default Pegasus labels with something that is 
    more representative of the site
    '''

    # local or file transfer means we need to use the execution
    # host name
    if t[endp + '_label'] == 'local' or \
       t[endp + '_url'].startswith('file://'):
        t[endp + '_label'] = extract_site(t['execution_host'])
        return

    # use the hostname in the url
    hostname = re.sub(r'^\w+://', '', t[endp + '_proto_host'])
    t[endp + '_label'] = extract_site(hostname)


def flip_event(event):
    '''
    Given a dict from ES, flip it for for what we want for ML - 
    this is a one-to-many transform (one job can have many transfers)

    See https://docs.google.com/document/d/1j5unwMUpc588cV5a_G9g664KLj_D-w12z12G602aVhA/edit
    '''
    transfers = []

    if not 'integrity_verification_attempts' in event:
        #pprint(event)
        #sys.exit(1)
        # ignore for now
        return transfers

    if 'local_dur' not in event:
        pprint(event)
        sys.exit(1)
    
    if 'jobtype' not in event:
        pprint(event)
        sys.exit(1)

    integrity = event['integrity_verification_attempts']

    for transfer in event['transfer_attempts']:
        t = transfer.copy()

        # missing lfn?
        if 'lfn' not in t:
            continue

        # remove some attributes
        t.pop('start')
        t.pop('duration')

        # data from the job
        t['root_xwf_id'] = event['root_xwf_id']
        t['job_id'] = event['job_id']
        t['end_time'] = event['ts']
    
        t['start_time'] = event['ts'] - event['local_dur']
        t['submit_host'] = event['submit_hostname']
        t['submit_user'] = event['wf_user']
        t['execution_host'] = safe_member(event, 'hostname')
        t['execution_user'] = safe_member(event, 'user')
        t['job_type'] = event['jobtype']
        t['job_exit_code'] = event['exitcode']
        #t['job_retry'] = event['']

        # some renames
        t['transfer_success'] = t.pop('success')

        # add integrity data
        i = find_integrity_data(t['lfn'], integrity)
        t['checksum_success'] = i['success']
        t['actual_checksum'] = i['sha256']
        t['expected_checksum'] = i['sha256_expected']
        if t['checksum_success']:
            t['expected_checksum'] = t['actual_checksum'] 

        # src proto and host
        t['src_proto_host'] = proto_host(t['src_url'])
        t['dst_proto_host'] = proto_host(t['dst_url'])

        fix_label(t, 'src')
        fix_label(t, 'dst')

        # scenario is just a cleaned up dag name
        t['scenario'] = re.sub('^[0-9]+-', '', event['dag'])
        t['scenario'] = re.sub('-0.dag$', '', t['scenario'])

        transfers.append(t)

    return transfers


def main():

    #configure command line option parser
    parser = optparse.OptionParser()

    parser.add_option("-s", "--start", action = "store", dest = "start",
                      help = "Start date")
    parser.add_option("-e", "--end", action = "store", dest = "end",
                      help = "End date")

    # Parse command line options
    (options, args) = parser.parse_args()

    start_dt = parse(options.start)
    end_dt = parse(options.end)

    client = Elasticsearch('https://galactica.isi.edu/es/', 
                           http_auth = (os.environ['ES_USERNAME'], os.environ['ES_PASSWORD']),
                           timeout=60000,
                           max_retries=3)

    # set up the CSV writer
    f = open('transfer-events.csv','w')
    w = csv.DictWriter(f, fieldnames=[
            'root_xwf_id',
            'job_id',
            'start_time',
            'end_time',
            'submit_host',
            'submit_user',
            'execution_host',
            'execution_user',
            'job_type',
            'job_exit_code',
            'bytes',
            'lfn',
            'src_label',
            'src_url',
            'src_proto_host',
            'dst_label',
            'dst_url',
            'dst_proto_host',
            'transfer_success',
            'checksum_success',
            'actual_checksum',
            'expected_checksum',
            'scenario'
        ])
    w.writeheader()
    
    current_dt = start_dt
    while current_dt < end_dt:

        results = False
        for event in get_events(client, current_dt):
            w.writerows(flip_event(event))  
            current_dt = parse(event['@timestamp']).replace(tzinfo=None)
            results = True

        # no results?
        if not results:
            current_dt = current_dt + datetime.timedelta(hours = 1)

    f.close()

if __name__=="__main__":
    main()
    
