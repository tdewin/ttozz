#!/usr/bin/python3

import argparse
import glob
import subprocess
import re
import math
import json
import os.path

def analyzeFiles(files,debug=False,segment_kb=256,superblock=6):
    segments = set()
    superblocks = set()

    fSort = []
    for f in files:
        fSort.append({"f":f,"t":os.path.getmtime(f)})
    fSort.sort(key=lambda x:x["t"])
    

    alldata_b = 0
    allsegments = 0
    
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

    for fS in fSort:
        f = fS["f"]
        fsegcount = 0
        filesize_b = 0
        fragcount = 0

        bmap = subprocess.Popen(["xfs_bmap",f], stdout=subprocess.PIPE, universal_newlines=True)
        
        intervals = []
        for i in bmap.stdout:
            m = re.search("\s+[0-9]+: \[[0-9]+\.\.[0-9]+\]: ([0-9]+)\.\.([0-9]+)",i)
            if m:
                startint = int(m.group(1))
                stopint = int(m.group(2))

                if len(intervals) > 0 and intervals[len(intervals)-1]["stopint"] == startint-1:
                    #print("colliding:",intervals[len(intervals)-1]["stopint"],startint)
                    intervals[len(intervals)-1]["stopint"] = stopint
                else:
                    intervals.append({
                        "startint": startint,
                        "stopint": stopint
                        })
            elif debug:
                print("ignoring bmap output line:",i.strip())
        if debug:
            print(f,intervals)

        for i in intervals:
                # we need to align the start so that the sets matches up
                startint = i["startint"]
                stopint = i["stopint"]

                #overaccount for regular segments, worst case 3 segments would be calculated for 1,01 segment 
                start = startint >> segmenting
                stop = (stopint >> segmenting) + 1
                
                intinterval = (stopint-startint)
                allsegments += intinterval >> segmenting

                #512 blocks
                #<<9 is like multiplying by 512
                frag_b = (intinterval<<9)
                filesize_b += frag_b
                fragcount += 1
                
                # get to superblock
                superstart = ((start >> superblock)+1) << superblock
                notAlreadyInSuperBlock = not ((start >> superblock) in superblocks) 
                while start <= superstart and start < stop:
                    if notAlreadyInSuperBlock:
                        segments.add(start)
                    fsegcount += 1
                    start += 1

                #skip in superblocks
                superstop = (stop >> superblock) << superblock
                while (start+sbsize) < superstop:
                    superblocks.add((start >>superblock))
                    fsegcount += sbsize
                    start += sbsize

                # if there are blocks left
                notAlreadyInSuperBlock = not ((start >> superblock) in superblocks) 
                while start < stop:
                    if notAlreadyInSuperBlock:
                        segments.add(start)
                    fsegcount += 1
                    start += 1



        alldata_b += filesize_b
        est = fsegcount*segment_b

        filesOut.append({
            "name":f,
            "segcount":fsegcount,
            "est_filesize_b":est,
            "filesize_b":filesize_b,
            "variance":est/filesize_b,
            "fragcount":fragcount
            })

    #remove overlapping segments from cleanup
    cleansegments = set()
    for s in segments:
        if not (s >> superblock) in superblocks:
            cleansegments.add(s)
    segments = cleansegments

    #All the file offsets and disk blocks are in units of 512-byte blocks or half a kb (/2)
    lsegc = len(segments)
    lsbc = len(superblocks)
    
    segcount = lsegc+(lsbc<<superblock)
    allsegcount = allsegments

    realusage_b = segcount*segment_b
    
    savings = allsegcount/segcount

    return {
                "realusage_b": realusage_b,
                "allusage_b":alldata_b,
                "savings": savings,
                "realsegcount": segcount,
                "allsegcount": allsegcount,
                "segment_b": segment_b,
                "regular_segments":lsegc,
                "superblock_segments":lsbc,
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
    print("Real Standalone Segments: %s" % (stats["regular_segments"]))
    print("Real Superblocks Segments: %s" % (stats["superblock_segments"]))

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
parser.add_argument('-S','--superblock', default=5,type=int,help="Magnitude of superblock, recommended to keep as is")
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

