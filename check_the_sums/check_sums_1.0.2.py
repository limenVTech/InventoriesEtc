#!/usr/bin/env python3

"""Script to compare Md5 output from VTechData with Md5's recorded in bagged data sets.
Created for Data Services, by L. I. Menzies, 2019-07-22.
"""

import argparse
import codecs
import csv
import tarfile
from os import linesep, listdir, path
from sys import exit
from time import strftime


def csv_sums(csvfile):
    """Extracts filenames, ids, and checksum hashes from the FedoraRepo master csv metadata file  and outputs a list of
    quadruples.
    """
    csv_hashes = []
    with open(csvfile, 'r', newline='') as input_csv:
        csv_reader = csv.DictReader(input_csv)
        for rows in csv_reader:
            csv_quadruple = (rows['filename'], rows['id'], rows['original_checksum'], 'n/a')
            csv_hashes.append(csv_quadruple)
    return csv_hashes


def bag_sums(bagdir):
    """Extracts filenames, ids, checksum hashes, and bag names from the BagIt generated manifest-md5.txt file and the
     DisseminatedMetadata...generic.csv file from each tarred bag and outputs two lists of quadruples.
    """
    bagit_hashes = []
    dissem_mdata = []
    uncounted = [
        'bag-info.txt', 'bagit.txt', 'manifest-md5.txt', 'manifest-sha512.txt', 'tagmanifest-md5.txt',
        'tagmanifest-sha512.txt', 'manifest.csv', 'README.rtf', 'Provenance.rtf'
    ]
    for item in listdir(bagdir):
        item_path = path.join(bagdir, item)
        if path.splitext(item)[-1] == '.tar':
            bag_file_count = 0  # The number of files in the bag
            total_bagit = 0  # The number of files in 'manifest-md5.txt'
            dissem_total = 0  # The number of files in 'DisseminatedMetadata...genericfile.csv'
            dissem_actual = 0  # Number of files in 'data/DisseminationContent/' minus the 2 CSVs
            tar = tarfile.open(item_path)
            for member in tar.getmembers():
                if member.isreg():  # Ignore directories
                    fname = member.name
                    if 'data' in fname:
                        bag_file_count += 1
                    if 'DisseminationContent' in fname:
                        if not 'DisseminatedMetadata' in fname:
                            dissem_actual += 1
                    if 'DisseminatedContent' in fname:
                        if not 'DisseminatedMetadata' in fname:
                            dissem_actual += 1
                    if path.basename(fname) == 'manifest-md5.txt':
                        bagit_manifest = codecs.getreader("utf-8")(tar.extractfile(fname))
                        for line in bagit_manifest:
                            row = []
                            blank = 'y'
                            for thing in line.split('  '):  # The delimiter is a double-space
                                if not thing == '':
                                    row.append(thing)
                                    blank = 'n'
                            if blank == 'n':
                                total_bagit += 1
                            file_name = path.basename(row[1]).split(linesep)[0]
                            bagit_quadruple = (file_name, 'n/a', row[0], item)
                            bagit_hashes.append(bagit_quadruple)
                    elif 'DisseminatedMetadata' in path.basename(fname) and 'generic' in path.basename(fname):
                        metadata = codecs.getreader("utf-8")(tar.extractfile(fname))
                        content = csv.DictReader(metadata)
                        for rows in content:
                            dissem_total += 1
                            dissem_quadruple = (rows['filename'], rows['id'], rows['checksum'], item)
                            dissem_mdata.append(dissem_quadruple)
            if not bag_file_count == total_bagit:
                print(f'**** There was an error in bag <{item}>. ****\n'
                      f'No. of files in bag: {bag_file_count}, \n'
                      f'No. in BagIt manifest: {total_bagit}, \n'
                      f'Quitting...\n')
                exit()  # Exits if the file counts don't match
            elif not dissem_total == dissem_actual:
                print(f'**** There was an error in bag <{item}>. ****\n'
                      f'Number of files in DisseminatedMetadata: {dissem_total}\n'
                      f'No. in data/DisseminatedContent/: {dissem_actual}\n'
                      f'Quitting...\n')
                exit()  # Exits if the file counts don't match
            else:
                print(f'----- {item} -----\n'
                      f'Total files in bag: {bag_file_count}\n'
                      f'Total files in BagIt manifest: {total_bagit}\n'
                      f'No. files in DisseminatedContent: {dissem_actual}\n'
                      f'No. files in DisseminatedMetadata: {dissem_total}')
    # Compare the checksums in the DisseminatedMetadata file with the one in the BagIt 'manifest-md5.txt' file
    for ck in dissem_mdata:
        is_there = 'n'
        for ha in bagit_hashes:
            if ck[0] == ha[0] and ck[3] == ha[3]:  # If the filename and bag name match, it
                is_there = 'y'  # checks the md5 sums from the two files
                break
        if is_there == 'y':
            if not ck[2] == ha[2]:
                print(f'**** There was an error with bag <{ck[3]}>. ****\n'
                      f'The md5 in the BagIt manifest for file: {ck[0]} \n'
                      f'does not match the one in the DisseminatedMetadata file.\n'
                      f'Quitting...\n')
                exit()
        elif is_there == 'n':
            print(f'**** There was an error with bag <{ck[3]}>. ****\n'
                  f'The file: {ck[0]}\n'
                  f'was not found in the BagIt manifest file.\n'
                  f'Quitting...\n')
            exit()
    return dissem_mdata


def check_sums(csvsums, bagsums, logdir):
    """Compares checksums and outputs logfile of successes and failures."""
    total = 0
    good = 0
    runtime = strftime('%Y%b%d%H%M%S')
    headerow = ['filename', 'bag_name', 'file_id', 'fedora_checksum', 'bagged_checksum', 'matches (y/n)', 'timestamp']
    logfile = open(path.join(logdir, f'Checksums_Log_{runtime}.csv'), 'w')
    log_writer = csv.DictWriter(logfile, fieldnames=headerow)
    log_writer.writeheader()
    for i in bagsums:
        found = False
        match = 'n'
        for t in csvsums:
            if i[0] in t and i[1] in t:
                if i[2] == t[2]:
                    good += 1
                    match = 'y'
                found = True
                total += 1
                break  # Breaks the loop at the first filename and id match
        if found == True:
            newrow = {}
            newrow['filename'] = i[0]
            newrow['bag_name'] = i[3]
            newrow['file_id'] = i[1]
            newrow['fedora_checksum'] = t[2]
            newrow['bagged_checksum'] = i[2]
            newrow['matches (y/n)'] = match
            newrow['timestamp'] = strftime("%Y-%m-%dT%H:%M:%S-04:00")
            log_writer.writerow(newrow)
    logfile.close()
    return [total, good]


def main():
    parser = argparse.ArgumentParser(description="Compare filenames and checksums from a master metadata spreadsheet, "
                                                 "output from FedoraRepo, with metadata extracted from bagged objects, "
                                                 "to ensure that items sent to Preservation are identical with those in"
                                                 " the repository.")
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
