#!/bin/bash
#depends on: apt-get install inotify-tools
SRCDIR="/mnt/backup"
TGTCACHE="/home/human/cache/"
SORTEDFRAG="/home/human/sortedfrag.py"


echo "Analyze later with"
echo "./sortedfrag-analyze.py -d $TGTCACHE/$SRCDIR/<jobdir>"
while read line
do
	ATTRFILE=$(echo $line | cut -f3 -d";")
	ATTRDIR=$(echo $line | cut -f2 -d";")
	echo "$ATTRDIR - $ATTRFILE"
	
	FRAGFILE="$TGTCACHE/$ATTRDIR/$ATTRFILE.frag"
	mkdir -p "$TGTCACHE/$ATTRDIR"
	"$SORTEDFRAG" -f "$ATTRDIR/$ATTRFILE" > "$FRAGFILE"
	echo "CREATED $FRAGFILE"
	
done < <(inotifywait -mr -q --timefmt '%d/%m/%y %H:%M' --include "(vbk|vib)" --event ATTRIB --format '%T;%w;%f'  $SRCDIR)

