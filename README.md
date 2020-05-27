# drivewiper

Wipe all data in the free space of a drive.

This program wipes free space of a drive by filling it with random binary
data. The random data is suitable for cryptographic use which means the
security of this program is guaranteed.

```
usage: drivewiper.py [-h] [-n NUMROUNDS] [-s] [-u {b,k,m,g,t}]
                     [--filesize FILESIZE] [--blocksize BLOCKSIZE]
                     [--namelength NAMELENGTH]
                     drive

Select a drive to wipe.

positional arguments:
  drive                 the drive to be wiped

optional arguments:
  -h, --help            show this help message and exit
  -n NUMROUNDS, --numrounds NUMROUNDS
                        the number of rounds to wipe the drive
  -s, --silent          silent mode
  -u {b,k,m,g,t}, --unit {b,k,m,g,t}
                        the unit used
  --filesize FILESIZE   the maximum size of files
  --blocksize BLOCKSIZE
                        the maximum block size to be written to a file
  --namelength NAMELENGTH
                        the length of the names of the created files
```

Example:
```
DriveWiper F: -n 3
```
