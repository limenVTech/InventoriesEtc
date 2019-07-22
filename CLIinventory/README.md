# CLIinventory

A quick command-line-interface inventory tool. Input is a path to a directory to be inventoried and a path to a directory where output will be stored. Output is a comma-separated-value spreadsheet that consists of one row per file and columns corresponding to the metadata for each file.

## Getting Started

Runs on Python 3. Download script and run:
    python3 CLIinventory.py

### Prerequisites

Required Python Modules: os, time, csv, io, hashlib, mimetypes, math

```
pip3 install hashlib
```

### Installing

Just download the script. No need to install anything except Python3 and the necessary modules.

```
python3 CLIinventory.py

What is the path to the directory to be inventoried (Do not include final slash)?
Input Path: /Volumes/some_nas/some_directory/item12345

What is the path to the directory where the results will be stored (Do not include final slash)?
Output Path: /Users/username/Desktop/inventories

Done.
```

## Running the tests

Test1: Run with filenames that include commas. See if the CSV cells turn out correctly.

Test2: Run on the same directory of files. See if checksums match.

Test3: Run on invalid paths. See if errors are thrown properly.

### Break down into end to end tests

n/a

### And coding style tests

n/a

## Deployment

Can be "frozen" with pyinstaller or similar tool.
Interactive GUI version is available (contact L. I . Menzies)

## Built With

* [Python3]
* [HashLib]
* [PyCharm]

## Contributing

n/a

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

* **L. I. Menzies** - *Initial work*

## License

n/a

## Acknowledgments

* BDPLinventory by L. I. Menzies


