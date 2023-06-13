#!/bin/sh
SRCDIR="/mnt/backup/Backup Job 1/"
TGTCACHE="/home/human/cache/"
SORTEDFRAG="./sortedfrag.py"
SORTEDFRAGANALYZE="./sortedfrag-analyze.py"

mkdir -p "$TGTCACHE/$SRCDIR"
find "$SRCDIR" -iname "*.v[bi][kb]" | while read f ; do  "$SORTEDFRAG" -f "$f" > "$TGTCACHE/$f.frag" ; done

"$SORTEDFRAGANALYZE" -d "$TGTCACHE/$SRCDIR" -b 4096
