# check_sums.py

A script to compare checksum hashes from FedoraRepo CSV output (VTData) with the checksum hashes contained in the "DisseminatedMetadata...genericfile.csv" of tarred, bagged data sets. Input is the spreadsheet, the directory that contains the tarred bags, and the directory where the log file will be created. Output is a log file with a list of the tarred bags that were checked and whether their checksum hashes match. 

## Getting Started

Runs on Python 3. Download script and run: 

```
python3 check_sums.py -s <SPREADSHEET> -b <BAGS DIRECTORY> -l <LOG DIRECTORY>
```

### Prerequisites

Required Python Modules: argparse, codecs, csv, tarfile, os, time

### Installing

Just download the script. No need to install anything except Python3 and the necessary modules.

```
python3 check_sums.py -s '<path-to-dir>/DataServices/2019-04-09_162054_genericfile.csv' -b '<path-to-dir>/DataServices/TarredBags' -l '<path-to-dir>/DataServices'

Of 21 total hashes checked, 21 were matches.
```

## Running the tests

Testing can be done by exporting CSV metadata from VTechData (FedoraRepo/ Samvera) and downloading several tarred, bagged data sets to a local machine. Then enter the paths to the CSV spreadsheet, the tarred bags, and the place where you want the log file to be into the command for check_sums.py and run it.

Test1: Run on data sets that contain files with the same names.

Test2: Run with checksum hashes that don't match. See if it catches them.

Test3: Run on files that contain non-Latin characters.

### Break down into end to end tests

n/a

### And coding style tests

n/a

## Deployment

Can be modified to compare checksum hashes output from other platforms.
Can be "frozen" with pyinstaller or similar tool.
Interactive GUI version can be produced (contact L. I . Menzies)

## Built With

* [Python3]
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

n/a


