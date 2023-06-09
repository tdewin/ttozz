#!/usr/bin/python3

import argparse
import glob
import subprocess
import re
import math

def analyzeDir(jobdir,segmenting,kilo,exponent):
    print("Dir: %s Segment Size: %d" % (jobdir,segmenting))
    files = glob.glob("%s/*.v[bi][kb]" % jobdir)

    segments = set()
    allsegcount = 0

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
                    allsegcount += 1
                    start += segmenting 
            #else:
            #    print("ignoring:",i.strip())

    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    segcount = len(segments)
    humanize = math.pow(kilo,exponent)
    suffix = ["K","M","G","T","P"]
    overlaps = segcount*segmenting/2/humanize
    fsreportusages = allsegcount*segmenting/2/humanize
    savings = allsegcount/segcount

    print("%s %sB (%d*%d*512); fs reported %s %sB; Savings %s:1" % (overlaps,suffix[exponent],segcount,segmenting,fsreportusages,suffix[exponent],savings))

parser = argparse.ArgumentParser(
                    prog='XFS TTOZZ',
                    description='Analyses block cloning',
                    epilog='Pass a directory')
parser.add_argument('-j','--jobdir', required=True)
parser.add_argument('-s','--segmenting', default=256,type=int,help="granularity of the calculation. Most accurate would be 1 but will take a long time. Use something above > 256 for scalability")
parser.add_argument('-b','--bytedivider', default=(1024),type=int,help="Default 1024 for converting bytes to human readable.")
parser.add_argument('-e','--expdivider',default=(2),type=int,help="Exponent to convert value to human readable (bytdivider)^expdivider. k=0,m=1,g=2,t=3,p=4")
args = parser.parse_args()
analyzeDir(args.jobdir,args.segmenting,args.bytedivider,args.expdivider)
