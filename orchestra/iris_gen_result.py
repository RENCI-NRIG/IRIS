#!/usr/bin/env python3
import csv
import os
import sys
import fnmatch
import yaml


def main():
    result_dir = sys.argv[1].rstrip("/")
    dict_label_ts = {}

    missing_uuids = set()
    found_uuids = set()
    ignored_uuids = set()
    wfs = {} # dict of workflows. key: root_wf_uuid, value: run+site

    for matched_file in fnmatch.filter(os.listdir(result_dir), '*run*_braindump.yml'):
        filepath = os.path.join(result_dir, matched_file)
        (run, site, _) = os.path.basename(filepath).split('_')
        with open(filepath, "r") as f:
            info = yaml.load(f)
            missing_uuids.add(info['root_wf_uuid'])
            wfs[info['root_wf_uuid']] = os.path.basename(filepath)

    with open(os.path.join(result_dir, 'root_wf_uuids.txt'), 'w+') as f:
        for k, v in wfs.items():
            f.write('{}: {}\n'.format(k,v))

    # parse corrupt timestamp logs
    for matched_file in fnmatch.filter(os.listdir(result_dir), '*run*_corrupt.log'):
        filepath = os.path.join(result_dir, matched_file)
        (label, run, _) = os.path.basename(filepath).split('_')
        with open(filepath, "r") as f:
            for line in f:
                if 'START' in line:
                    start_time = int(line.split()[0])
                elif 'END' in line:
                    end_time = int(line.split()[0])
        corrupt_rate = ''
        if '+' in label:
            (label, corrupt_rate) = label.split('+')
        dict_label_ts[(label, corrupt_rate)] = (start_time, end_time)

    # read 'transfer-events.csv' and generate new csv
    incsv_file = os.path.join(result_dir, 'transfer-events.csv')
    outcsv_file = os.path.join(result_dir, os.path.basename(result_dir) + '_full.csv')
    outcsv_file_2 = os.path.join(result_dir, os.path.basename(result_dir) + '.csv')
    with open(incsv_file) as incsv, open(outcsv_file, 'w', newline='') as outcsv, \
            open(outcsv_file_2, 'w', newline='') as outcsv2:
        reader = csv.DictReader(incsv)
        headers = reader.fieldnames
        writer = csv.DictWriter(outcsv, fieldnames=headers + ['corrupt_label'] + ['corrupt_start'] + ['corrupt_end'] + ['corrupt_rate'])
        writer2 = csv.DictWriter(outcsv2, fieldnames=headers + ['corrupt_label'] + ['corrupt_start'] + ['corrupt_end'] + ['corrupt_rate'])
        writer.writeheader()
        writer2.writeheader()
        for row in reader:
            if row['root_xwf_id'] in missing_uuids:
                missing_uuids.remove(row['root_xwf_id'])

            if row['root_xwf_id'] not in wfs.keys():
                ignored_uuids.add(row['root_xwf_id'])
                continue
            else:
                found_uuids.add(row['root_xwf_id'])

            row_start = int(row['start_time'])
            row_end = int(row['end_time'])
            corrupt_label = ''
            corrupt_start = ''
            corrupt_end = ''
            corrupt_rate = ''
            for key, ts in dict_label_ts.items():
                # ts[0] = corrupt start time, ts[1] = corrupt end time
                if ((row_start <= ts[0] <= row_end)
                        or (row_start <= ts[1] <= row_end)
                        or (ts[0] < row_start and row_end < ts[1])):
                    corrupt_label += key[0] + ' '   # append in case overlap which should not happen
                    corrupt_start = ts[0]
                    corrupt_end = ts[1]
                    corrupt_rate = key[1]
            row.update({'corrupt_label': corrupt_label})
            row.update({'corrupt_start': corrupt_start})
            row.update({'corrupt_end': corrupt_end})
            row.update({'corrupt_rate': corrupt_rate})

            # output all corruption information to the full.csv
            writer.writerow(row)

            # for concise version output .csv, just mark the rows with incorrect checksum
            # (clear the corruption labels for the rows with correct checksum for compute node)
            if '.Link' not in corrupt_label and 'True' in row['checksum_success']:
                row.update({'corrupt_label': ''})
                row.update({'corrupt_start': ''})
                row.update({'corrupt_end': ''})
                row.update({'corrupt_rate': ''})
            writer2.writerow(row)
    print('csv generated:\n{}'.format(outcsv_file))
    print(outcsv_file_2)

    print('root_wf_uuids:{}'.format(len(wfs)))
    print('found_uuids/ignored_uuids:{}/{}'.format(
        len(found_uuids),
        len(ignored_uuids)))
    print('missing_uuids:{}'.format(len(missing_uuids)))
    for uuid in missing_uuids:
        print('{}: {}\n'.format(uuid, wfs[uuid]))

    with open(os.path.join(result_dir, 'parsed_uuids.txt'), 'w+') as of:
        of.write('root_wf_uuids: {}\n'.format(len(wfs)))
        of.write(repr(wfs.keys()))
        of.write('\nfound_uuids: {}\n'.format(len(found_uuids)))
        of.write(repr(found_uuids))
        of.write('\nignored_uuids: {}\n'.format(len(ignored_uuids)))
        of.write(repr(ignored_uuids))
        of.write('\nmissing_uuids: {}\n'.format(len(missing_uuids)))
        for uuid in missing_uuids:
            of.write('{}: {}\n'.format(uuid, wfs[uuid]))

if __name__ == "__main__":
    main()
