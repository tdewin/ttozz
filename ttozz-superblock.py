#!/usr/bin/python3

import argparse
import glob
import subprocess
import re
import math
import json

def analyzeFiles(files,debug=False,segment_kb=256,superblock=6):
    segments = set()
    superblocks = set()

    allsegcount = 0

    
    if len(files) < 1:
        raise Exception("Could not find any files, make sure you pass directory with vbk/vib files")
        
    filesOut = []

    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    # bit shifting >> 1 make a 512 a 1kb
    # thus we add +1 to convert 1kb
    # for all above 1kb, we need to know how much we need to shift back and forward
    # we do this by taking log2()
    # eg 256 => log2(256) => int(math.log2(256)) >> 8
    # 256 >> 8 = 1
    # 312 >> 8 = 1
    # 512 >> 8 = 2
    # 799 >> 8 = 3
    # 1024 >> 8 = 4

    segmenting = int(math.log2(segment_kb))+1
    sbsize = (1 << superblock)

    segment_b = segment_kb*1024

    for f in files:
        fsegcount = 0
        bmap = subprocess.Popen(["xfs_bmap",f], stdout=subprocess.PIPE, universal_newlines=True)
        
        for i in bmap.stdout:
            m = re.search("\s+[0-9]+: \[[0-9]+\.\.[0-9]+\]: ([0-9]+)\.\.([0-9]+)",i)
            if m:
                # we need to align the start so that the sets matches up
                start = int(m.group(1)) >> segmenting
                stop = (int(m.group(2)) >> segmenting) + 1
                superstop = stop >> superblock

                while start < stop:
                    superstart = start >> superblock
                    if superstart < superstop:
                        superblocks.add(superstart)
                    
                    if not superstart in superblocks:
                        segments.add(start)
                        fsegcount += 1
                        start += 1
                    else:
                        start += sbsize
                        fsegcount += sbsize
            elif debug:
                print("ignoring bmap output line:",i.strip())

        allsegcount += fsegcount
        filesOut.append({
            "name":f,
            "segcount":fsegcount,
            "est_filesize":fsegcount*segment_b
            })


    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    segcount = len(segments)+(len(superblocks)<<superblock)
    realusage = segcount*segment_b
    allusage = allsegcount*segment_b
    savings = allsegcount/segcount

    return {
                "realusage_b": realusage,
                "allusage_b":allusage,
                "savings": savings,
                "realsegcount": segcount,
                "allsegcount": allsegcount,
                "segment_b": segment_b,
                "files":filesOut
    }

def analyzeDir(jobdir,debug=False,segmenting=256,superblock=6,isrepo=0):
    files = []
    if isrepo == 1:
        files = glob.glob("%s/**/*.v[bi][kb]" % jobdir,recursive=True)
    else:
        files = glob.glob("%s/*.v[bi][kb]" % jobdir)
    return analyzeFiles(files,debug,segmenting,superblock)

def analyzeAndPrintJSONDir(jobdir,debug=False,segmenting=256,superblock=6,isrepo=0):
    print(json.dumps(analyzeDir(jobdir,debug,segmenting,superblock,isrepo)))

def analyzeAndPrintDir(jobdir,debug=False,segmenting=256,superblock=6,isrepo=0,kilo=1024,exponent=3):
    #correcting if you want to use /1000
    humanize = math.pow(kilo,exponent)
    suffix = ["","K","M","G","T","P"]
    s = suffix[exponent]

    print("Dir: %s" % (jobdir))
    print("Segments: %s" % (segmenting))
    stats = analyzeDir(jobdir,debug,segmenting,superblock,isrepo)
    print("Real Usage %sB: %s" % (s,(stats["realusage_b"]/humanize)))
    print("All Usage %sB: %s" % (s,(stats["allusage_b"]/humanize)))
    print("Savings: %s" % (stats["savings"]))
    
    print("Real Segments: %s" % (stats["realsegcount"]))
    print("All Segments: %s" % (stats["allsegcount"]))
    print("Segment in bytes: %s" % (stats["segment_b"]))
    print("Superblock in bytes: %s" % (stats["segment_b"]<<superblock))

# 3-2-1-0-0
parser = argparse.ArgumentParser(
                    prog='XFS TTOZZ',
                    description='Analyses block cloning',
                    epilog='Pass a directory')
parser.add_argument('-j','--jobdir', required=True)
parser.add_argument('-o','--output', default="human")
parser.add_argument('-s','--segmenting', default=64,type=int,help="Granularity of the calculation. In KB, lower then 4kb doesn't make sense (4kb XFS blocksize)")
parser.add_argument('-S','--superblock', default=6,type=int,help="Magnitude of superblock, recommended to keep as is")
parser.add_argument('-b','--bytedivider', default=(1024),type=int,help="Default 1024 for converting bytes to human readable.")
parser.add_argument('-e','--expdivider',default=(3),type=int,help="Exponent to convert value to human readable (bytdivider)^expdivider. k=1,m=2,g=3,t=4,p=5")
parser.add_argument('--debug', default=False)
parser.add_argument('--repo', default=0,help="Not recommended, pass 1 for enabling this",type=int)
args = parser.parse_args()
if args.debug:
    print(args)
if args.output == "human":
    analyzeAndPrintDir(args.jobdir,args.debug,args.segmenting,args.superblock,args.repo,args.bytedivider,args.expdivider)
elif args.output == "json":
    analyzeAndPrintJSONDir(args.jobdir,args.debug,args.segmenting,args.superblock,args.repo)

