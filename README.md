Download
```sh
wget https://raw.githubusercontent.com/tdewin/ttozz/main/ttozz.py
chmod +x ttozz.py
```

Run against a job dir
```sh
sudo ./ttozz.py -j /mnt/backup/Backup\ Job\ 1/ -s 2048
```

Should output something like this
```
Dir: /mnt/backup/Backup Job 1/
Segments: 2048
Real Usage GB: 3.947265625
All Usage GB: 6.37890625
Savings: 1.6160316674913409
Real Segments: 4042
All Segments: 6532
Segment in bytes: 1048576
```

```
du -h /mnt/backup
6.4G    /mnt/backup/Backup Job 1
6.4G    /mnt/backup
```

```
df -h /mnt/backup
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdb1       100G  4.7G   96G   5% /mnt/backup
```

* real usage =~ should be related to df on a disk level. Do take into account that XFS itself, even if empty will still use some space for meta data.
* all usage =~ should be related to du for the folder
* savings = all usage / real usage; basically the compression level x:1. For example 1.6 in the example basically means 1.6:1 savings (low because of test lab only having 2 full backups)
* segment in bytes = basically blocksize. xfs_bmap uses 512 bytes for boundaries, thus if you use a -s 2048, you get 2048*512 = 1048576 bytes or 1mb block size


Alternatively use -o json parameter to get some more debug info
```
{
  "realusage_kb": 4139008,
  "allusage_kb": 6688768,
  "savings": 1.6160316674913409,
  "realsegcount": 4042,
  "allsegcount": 6532,
  "segment_b": 1048576,
  "files": [
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-06-09T115813_C9E3.vib",
      "segcount": 1551,
      "est_filesize": 1626341376
    },
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-05-15T144450_E57C.vbk",
      "segcount": 2478,
      "est_filesize": 2598371328
    },
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-05-15T220007_5A06.vib",
      "segcount": 4,
      "est_filesize": 4194304
    },
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-06-09T103701_F73B.vib",
      "segcount": 4,
      "est_filesize": 4194304
    },
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-06-09T104205_FFBE.vbk",
      "segcount": 2486,
      "est_filesize": 2606759936
    },
    {
      "name": "/mnt/backup/Backup Job 1/forbackup.51D2023-06-09T135947_4C96.vib",
      "segcount": 9,
      "est_filesize": 9437184
    }
  ]
}
```