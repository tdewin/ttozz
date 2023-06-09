#!/usr/bin/python3

import argparse
import glob
import subprocess
import re

def analyzeDir(jobdir,segmenting):
    print("Dir: %s Segment Size: %d" % (jobdir,segmenting))
    files = glob.glob("%s/*.v[bi][kb]" % jobdir)

    segments = set()

    for f in files:
        bmap = subprocess.Popen(["xfs_bmap",f], stdout=subprocess.PIPE, universal_newlines=True)

        for i in bmap.stdout:
            m = re.search("\s+[0-9]+: \[[0-9]+\.\.[0-9]+\]: ([0-9]+)\.\.([0-9]+)",i)
            if m:
                # we need to align the start so that the sets matches up
                start = (int(m.group(1))//segmenting)*segmenting
                stop = int(m.group(2))
                while start < stop:
                    segments.add(start)
                    start += segmenting 
            #else:
            #    print("ignoring:",i.strip())

    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    overlaps = len(segments)*segmenting/2/1024/1024
    print(overlaps)

parser = argparse.ArgumentParser(
                    prog='XFS TTOZZ',
                    description='Analyses block cloning',
                    epilog='Pass a directory')
parser.add_argument('-j','--jobdir', required=True)
parser.add_argument('-s','--segmenting', default=256,type=int)
args = parser.parse_args()
analyzeDir(args.jobdir,args.segmenting)
