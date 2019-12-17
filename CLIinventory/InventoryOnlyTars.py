#!/usr/local/bin/python3

"""
This is a command-line-interface inventory tool. It is based largely on the
BDPLinventory tool created by L. I. Menzies.
Created: 2019-03-07
Last modified: 2019-03-25 by L. I. Menzies
"""

import csv
import hashlib
import io
import math
import mimetypes
import operator
from os import walk, stat, remove
from os.path import basename, dirname, isdir, join, relpath, splitext
from time import strftime, localtime

CHUNKSIZE = io.DEFAULT_BUFFER_SIZE

def md5hash(file_name):
    """ Generate SHA3-256 hashes. """
    hash_md5 = hashlib.md5()
    try:
        with open(file_name, "rb") as md5file:
            for chunks in iter(lambda: md5file.read(CHUNKSIZE), b""):
                hash_md5.update(chunks)
    except OSError:
        return "OS Error"
    return hash_md5.hexdigest()

def sha3hash(filname):
    """ Generate SHA3-256 hashes. """
    hash_sha3 = hashlib.sha3_256()
    try:
        with open(filname, "rb") as sha3file:
            for chunks in iter(lambda: sha3file.read(CHUNKSIZE), b""):
                hash_sha3.update(chunks)
    except OSError:
        return "OS Error"
    return hash_sha3.hexdigest()


def convert_size(size):
    """ Make file sizes human readable. """
    if (size == 0):
        return '0B'
    # size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    # i = int(math.floor(math.log(size,1024)))
    # p = math.pow(1024,i)
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1000)))
    p = math.pow(1000, i)
    s = round(size / p, 2)
    return '%s%s' % (s, size_name[i])


def run_inventory(indir, outdir):
    """ Run the inventory and output as Inv_<name>_<datetime>.csv. """
    filecounter = 0
    dsstore_count = 0
    nottar = 0
    inv_path = join(outdir, f'Inventory{strftime("%Y%b%d_%H%M%S")}temp.csv')
    inventory = open(inv_path, 'w')
    colnames = ['No.', 'Filename', 'RelPath', 'Filesize', 'Filetype', 'C-Time',
                'Modified', 'Accessed', 'MD5', 'MD5-Time', 'SHA3_256',
                'SHA3-Time','=>', 'mode', 'inode', 'device',
                'enlink', 'user', 'group']
    writeCSV = csv.writer(inventory)
    writeCSV.writerow(colnames)
    for base, dirs, files in walk(indir):
        for name in files:
            filepathname = join(base, name)
            # Ignore or delete .DS_Store Files
            if basename(filepathname) == '.DS_Store':
                # remove(filepathname)
                dsstore_count += 1
            elif not basename(filepathname) == '.DS_Store':
                if 'tar' in name.split('.')
                    filecounter += 1
                    rownum = str(filecounter)
                    statinfo = stat(filepathname)
                    filesize = statinfo[6]
                    csize = convert_size(filesize)
                    filemime = str(mimetypes.guess_type(filepathname)[0])
                    filectime = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_ctime))
                    # Note: On Windows, ctime is "date created" but on Unix it is
                    # "change time", i.e. the last time the metadata was changed.
                    modifdate = strftime("%Y.%m.%d %H:%M:%S",
                                         localtime(statinfo.st_mtime))
                    accessdate = strftime("%Y.%m.%d %H:%M:%S",
                                          localtime(statinfo.st_atime))
                    md5sum = md5hash(filepathname)
                    md5time = strftime("%Y.%m.%d %H:%M:%S")
                    sha3sum = sha3hash(filepathname)
                    sha3time = strftime("%Y.%m.%d %H:%M:%S")
                    filemode = str(statinfo.st_mode)
                    fileino = str(statinfo.st_ino)
                    filedevice = str(statinfo.st_dev)
                    filenlink = str(statinfo.st_nlink)
                    fileuser = str(statinfo.st_uid)
                    filegroup = str(statinfo.st_gid)
                    showpath = relpath(filepathname, dirname(indir))
                    newrow = [rownum, name, showpath, csize, filemime, filectime,
                                modifdate, accessdate, md5sum, md5time, sha3sum,
                                sha3time, ' ', filemode, fileino, filedevice,
                                filenlink, fileuser, filegroup]
                    writeCSV.writerow(newrow)
                    print(f'\rProgress: {filecounter} Files', end='')
                else:
                    nottar += 1
    inventory.close()
    print(f'\nSkipped {dsstore_count} \'.DS_Store\' files.')
    print(f'Skipped {nottar} non-tar-archive files.\n')
    return inv_path


def sort_inventory(unsorted_file, in_dir):
    print(f'Sorting Data... ')
    output_path = join(dirname(unsorted_file), f'Inventory_{basename(in_dir)}_{strftime("%Y%b%d_%H%M%S")}.csv')
    with open(unsorted_file, 'r') as un_csv:
        reading = csv.DictReader(un_csv)
        headers = reading.fieldnames
        sorted_data = sorted(reading, key=lambda row: row['RelPath'], reverse=False)
    with open(output_path, 'w') as out_csv:
        writing = csv.DictWriter(out_csv, fieldnames=headers)
        writing.writeheader()
        n = 1
        for rrows in sorted_data:
            rrows['No.'] = str(n)
            n += 1
            writing.writerow(rrows)
    remove(unsorted_file)
    return output_path


def main():
    print('What is the path to the directory to be inventoried (Do not include final slash)? ')
    invpath = input('Input Path: ')
    print('What is the path to the directory where the results will be stored (Do not include final slash)? ')
    outputdir = input('Output Path: ')
    print('\n')
    if not isdir(invpath) or not isdir(outputdir):
        print(f'Error: Could not find the input directory:\n    \'{invpath}\'\nor output directory:\n    \'{workdir}\'\nQuitting...')
    else:
        temp_inv = run_inventory(invpath, outputdir)
        inventory_sorted = sort_inventory(temp_inv, invpath)
        print(f'\nOutput File: {inventory_sorted}')
    print('\nDone.\n')


if __name__ == "__main__":
    main()
