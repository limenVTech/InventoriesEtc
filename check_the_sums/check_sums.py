#!/usr/bin/env python3

"""Script to compare Md5 output from VTechData with Md5's recorded in bagged data sets.
Created for Data Services, by L. I. Menzies, 2019-07-22.
"""


import argparse
import codecs
import csv
import tarfile
from os import listdir, path
from time import strftime


def csv_sums(csvfile):
    """Reduces CSV input to only the filename, Md5_hash, and id columns."""
    csv_hashes = []
    with open(csvfile, 'r', newline='') as input_csv:
        csv_reader = csv.DictReader(input_csv)
        for rows in csv_reader:
            csv_triple = (rows['filename'], rows['id'], rows['original_checksum'])
            csv_hashes.append(csv_triple)
    return csv_hashes


def bag_sums(bagdir):
    """Extracts file names and checksum hashes from manifests of tarred bags and outputs a dictionary."""
    bag_hashes = []
    for item in listdir(bagdir):
        item_path = path.join(bagdir, item)
        if path.splitext(item)[-1] == '.tar':
            tar = tarfile.open(item_path)
            for name in tar.getnames():
                if 'DisseminatedMetadata' in path.basename(name) and 'generic' in path.basename(name):
                    metadata = codecs.getreader("utf-8")(tar.extractfile(name))
                    content = csv.DictReader(metadata)
                    for row in content:
                        bagged_triple = (row['filename'], row['id'], row['checksum'])
                        bag_hashes.append(bagged_triple)
    return bag_hashes


def check_sums(csvsums, bagsums, logdir):
    """Compares checksums and outputs logfile of successes and failures."""
    total = 0
    good = 0
    runtime = strftime('%Y%b%d%H%M%S')
    headerow = ['filename', 'file_id', 'fedora_checksum', 'bagged_checksum', 'matches (y/n)', 'timestamp']
    logfile = open(path.join(logdir, f'Checksums_Log_{runtime}.csv'), 'w')
    log_writer = csv.DictWriter(logfile, fieldnames=headerow)
    log_writer.writeheader()
    for i in csvsums:
        found = False
        match = 'n'
        for t in bagsums:
            if i[0] in t and i[1] in t:
                if i[2] == t[2]:
                    good += 1
                    match = 'y'
                found = True
                total += 1
                break # Breaks the loop at the first filename and id match
        if found == True:
            newrow = {}
            newrow['filename'] = i[0]
            newrow['file_id'] = i[1]
            newrow['fedora_checksum'] = i[2]
            newrow['bagged_checksum'] = t[2]
            newrow['matches (y/n)'] = match
            newrow['timestamp'] = strftime("%Y-%m-%dT%H:%M:%S-04:00")
            log_writer.writerow(newrow)
    logfile.close()
    return [total, good]


def main():
    parser = argparse.ArgumentParser(
        description="Compare filenames and checksums from a spreadsheet with metadata extracted from bagged objects.")
    parser.add_argument("-s", '--spreadsheet', help="Path to input spreadsheet", required=True)
    parser.add_argument("-b", '--bags', help="Path to directory of bagged objects", required=True)
    parser.add_argument("-l", '--log', help="Path to directory where the log will be placed", required=True)
    args = vars(parser.parse_args())
    in_csv = args["spreadsheet"]
    bags_dir = args["bags"]
    log_directory = args["log"]
    if path.exists(in_csv) and path.isdir(bags_dir) and path.isdir(log_directory):
        csv_list = csv_sums(in_csv)
        bag_list = bag_sums(bags_dir)
        total_sums, good_sums = check_sums(csv_list, bag_list, log_directory)
        print(f'Of {str(total_sums)} total hashes checked, {str(good_sums)} were matches.')
    else:
        print(f'There was an error with your input.')


if __name__ == "__main__":
    main()

