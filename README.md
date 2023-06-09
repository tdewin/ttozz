Make executable
```sh
chmod +x ttozz.py
```

Run against a job dir
```sh
./ttozz.py -j /mnt/backup/Backup\ Job\ 1/ -s 4096
```

Should output something like this
```
Dir: /mnt/backup/Backup Job 1/
Segments: 4096
Real Usage GB: 3.9453125
All Usage GB: 6.400390625
Savings: 1.6222772277227724
Real Segments: 2020
All Segments: 3277
Segment in bytes: 2097152
```