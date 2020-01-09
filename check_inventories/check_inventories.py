#!/usr/bin/env python3

"""Script to compare checksums in two inventory files.
Created for Data Services, by L. I. Menzies, 2020-01-09.
"""

import argparse
import codecs
import csv
import tarfile
from os import linesep, listdir, path
from sys import exit
from time import strftime


def csv_sums(csvfile):
    """Extracts filenames, paths, and checksum hashes from inventory csv created by
    CLIinventory.py and outputs a list of quadruples.
    """
    csv_hashes = []
    with open(csvfile, 'r', newline='') as input_csv:
        csv_reader = csv.DictReader(input_csv)
        for rows in csv_reader:
            longpath = rows['RelPath']
            shortpath = longpath
            while '-tarred' in shortpath:
                shortpath = path.dirname(shortpath)
            trunc_path = path.relpath(longpath, shortpath)
            csv_quadruple = (rows['Filename'], trunc_path, rows['MD5'], rows['SHA3_256'])
            csv_hashes.append(csv_quadruple)
    return csv_hashes


def check_sums(csv1sums, csv2sums, logdir):
    """Compares checksums and outputs logfile of successes and failures."""
    total = 0
    good = 0
    runtime = strftime('%Y%b%d%H%M%S')
    headerow = ['filename', 'short_path', 'md5_csv1', 'md5_csv2', 'sha3_256_csv1', 'sha3_256_csv2', 'matches (y/n)', 'timestamp']
    logfile = open(path.join(logdir, f'Checksums_Log_{runtime}.csv'), 'w')
    log_writer = csv.DictWriter(logfile, fieldnames=headerow)
    log_writer.writeheader()
    for i in csv2sums:
        found = False
        match = 'n'
        for t in csv1sums:
            if i[0] in t and i[1] in t:
                if i[2] == t[2] and i[3] == t[3]:
                    good += 1
                    match = 'y'
                found = True
                total += 1
                break  # Breaks the loop at the first filename and path match
        if found == True:
            newrow = {}
            newrow['filename'] = i[0]
            newrow['short_path'] = i[1]
            newrow['md5_csv1'] = t[2]
            newrow['md5_csv2'] = i[2]
            newrow['sha3_256_csv1'] = t[3]
            newrow['sha3_256_csv2'] = i[3]
            newrow['matches (y/n)'] = match
            newrow['timestamp'] = strftime("%Y-%m-%dT%H:%M:%S-04:00")
            log_writer.writerow(newrow)
    logfile.close()
    return [total, good]


def main():
    parser = argparse.ArgumentParser(description="Compare filenames and checksums in two inventory CSVs.")
    parser.add_argument("-csv1", '--inventory1', help="Path to inventory 1", required=True)
    parser.add_argument("-csv2", '--inventory2', help="Path to inventory 2", required=True)
    parser.add_argument("-l", '--log', help="Path to directory where log output will be placed", required=True)
    args = vars(parser.parse_args())
    in_csv_1 = args["inventory1"]
    in_csv_2 = args["inventory2"]
    log_directory = args["log"]
    if path.exists(in_csv_1) and path.exists(in_csv_2) and path.isdir(log_directory):
        csv1_list = csv_sums(in_csv_1)
        csv2_list = csv_sums(in_csv_2)
        total_sums, good_sums = check_sums(csv1_list, csv2_list, log_directory)
        print(f'Of {str(total_sums)} total hashes checked, {str(good_sums)} were matches.')
    else:
        print(f'There was an error with your input.')


if __name__ == "__main__":
    main()
