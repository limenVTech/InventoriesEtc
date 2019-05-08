#!/usr/bin/env python3
"""
Script to create a transfer manifest as a CSV list of files and checksums.
"""


import argparse
import io
import hashlib
from time import strftime
from os import getcwd, path, remove, walk


def sha3_hash(filname):
    """ Generate SHA3-256 hashes. """
    chunksize = io.DEFAULT_BUFFER_SIZE
    hash_sha3 = hashlib.sha3_256()
    with open(filname, "rb") as sha3file:
        for chunks in iter(lambda: sha3file.read(chunksize), b""):
            hash_sha3.update(chunks)
    return hash_sha3.hexdigest()


def main(indir):
    num_files = 0
    outdir = getcwd()
    compfile = open(path.join(outdir, f'Transfer_{path.basename(indir)}_{strftime("%m%d_%H%M%S")}.csv'), 'w')
    sums = []
    for base, dirs, files in walk(indir):
        for name in files:
            pathname = path.join(base, name)
            if path.basename(pathname) == '.DS_Store':
                remove(pathname)
            elif not path.basename(pathname) == '.DS_Store':
                sha3sum = sha3_hash(pathname)
                sums.append([name,sha3sum])
                num_files += 1
    sums.sort()
    for r in sums:
        compfile.write(f"{r[0]},{r[1]}\n")
    compfile.close()
    return num_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate checksum hashes for all files in given directory.")
    parser.add_argument("dir_path", type=str, help="Path to input directory")
    args = parser.parse_args()
    in_dir = args.dir_path
    if path.exists(in_dir):
        no_items = main(in_dir)
        print(f"Checksummed {no_items} items.")
    else:
        print("Error. Folder not found.")
