#!/usr/bin/python3

import argparse
import glob
import subprocess
import re
import math

def analyzeDir(jobdir,debug,segmenting,isrepo):
    files = []
    if isrepo == 1:
        files = glob.glob("%s/**/*.v[bi][kb]" % jobdir,recursive=True)
    else:
        files = glob.glob("%s/*.v[bi][kb]" % jobdir)

    segments = set()
    allsegcount = 0
    
    if len(files) < 1:
        raise Exception("Could not find any files, make sure you pass directory with vbk/vib files")
        
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
            elif debug:
                print("ignoring bmap output line:",i.strip())

    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    segcount = len(segments)
    realusage = segcount*segmenting/2
    allusage = allsegcount*segmenting/2
    savings = allsegcount/segcount

    return {
                "realusage_kb": realusage,
                "allusage_kb":allusage,
                "savings": savings,
                "realsegcount": segcount,
                "allsegcount": allsegcount,
                "segment_b": segmenting*512,
    }


def analyzeAndPrintDir(jobdir,debug,segmenting,isrepo,kilo,exponent):
    #correcting if you want to use /1000
    humanize = math.pow(kilo,exponent)/1024
    suffix = ["","K","M","G","T","P"]
    s = suffix[exponent]

    print("Dir: %s" % (jobdir))
    print("Segments: %s" % (segmenting))
    stats = analyzeDir(jobdir,debug,segmenting,isrepo)

    print("Real Usage %sB: %s" % (s,(stats["realusage_kb"]/humanize)))
    print("All Usage %sB: %s" % (s,(stats["allusage_kb"]/humanize)))
    print("Savings: %s" % (stats["savings"]))
    
    print("Real Segments: %s" % (stats["realsegcount"]))
    print("All Segments: %s" % (stats["allsegcount"]))
    print("Segment in bytes: %s" % (stats["segment_b"]))

parser = argparse.ArgumentParser(
                    prog='XFS TTOZZ',
                    description='Analyses block cloning',
                    epilog='Pass a directory')
parser.add_argument('-j','--jobdir', required=True)
parser.add_argument('-s','--segmenting', default=256,type=int,help="granularity of the calculation. Most accurate would be 1 but will take a long time. Use something above > 256 for scalability")
parser.add_argument('-b','--bytedivider', default=(1024),type=int,help="Default 1024 for converting bytes to human readable.")
parser.add_argument('-e','--expdivider',default=(3),type=int,help="Exponent to convert value to human readable (bytdivider)^expdivider. k=1,m=2,g=3,t=4,p=5")
parser.add_argument('--debug', default=False)
parser.add_argument('--repo', default=0,help="Not recommended, pass 1 for enabling this",type=int)
args = parser.parse_args()
if args.debug:
    print(args)
analyzeAndPrintDir(args.jobdir,args.debug,args.segmenting,args.repo,args.bytedivider,args.expdivider)
