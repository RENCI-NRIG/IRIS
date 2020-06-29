#!/usr/bin/env python3
import csv
import os
import sys
import fnmatch


def main():
    result_dir = sys.argv[1].rstrip("/")
    dict_label_ts = {}

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
    outcsv_file = os.path.join(result_dir, os.path.basename(result_dir) + '.csv')
    with open(incsv_file) as incsv, open(outcsv_file, 'w', newline='') as outcsv:
        reader = csv.DictReader(incsv)
        headers = reader.fieldnames
        writer = csv.DictWriter(outcsv, fieldnames=headers + ['corrupt_label'] + ['corrupt_start'] + ['corrupt_end'] + ['corrupt_rate'])
        writer.writeheader()
        for row in reader:
            if row['lfn'] == 'job_sh':
                continue
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
            writer.writerow(row)
    print('csv generated:\n{}'.format(outcsv_file))


if __name__ == "__main__":
    main()
