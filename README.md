Make executable
```sh
chmod +x ttozz.py
```

Run against a job dir
```sh
./ttozz.py -j "/mnt/backup/Backup Job 1/" -s 1024
```

Should output something like this
```
Dir: /mnt/backup/Backup Job 1/ Segment Size: 1024
3.9365234375 GB (8062*1024*512); fs reported 6.35546875 GB; Savings 1.6144877201686927:1
```