#!/usr/bin/python3

import argparse
import subprocess
import re

def analyzeFile(file):
        #bmap seems wrong?
        #bmap = subprocess.Popen(["xfs_bmap",file], stdout=subprocess.PIPE, universal_newlines=True)
        bmap = subprocess.Popen(["filefrag","-e",file], stdout=subprocess.PIPE, universal_newlines=True)

        ind = []
        mapblks = {}

        blks = 0
        blksize = 4096

        for ln in bmap.stdout:
            #bmap regex
            #m = re.search("^\s*[0-9]+:\s+([0-9]+)\.\.([0-9]+)\s+: ([0-9]+)\.\.([0-9]+)",i)
            m = re.search("^\s*[0-9]+:\s*([0-9]+)\.\.\s*([0-9]+):\s*([0-9]+)\.\.\s*([0-9]+):\s*([0-9]+)",ln)
            if m:
                # we need to align the start so that the sets matches up
                vcnstart = int(m.group(1))
                vcnend = int(m.group(2))
                lcnstart = int(m.group(3))
                lcnend = int(m.group(4))
                
                #block 0..0 is still 1 block, block 0
                blks += (lcnend-lcnstart)+1

                ind.append(lcnstart)
                mapblks[lcnstart] = {
                        "vs":vcnstart,
                        "ve":vcnend,
                        "ls":lcnstart,
                        "le":lcnend
                }
            else:
                m = re.search("blocks of ([0-9]+) bytes",ln)
                if m:
                    blksize = int(m.group(1))

        ind.sort()
        
        sortedAndMergedBlks = []
        p = 0

        for i in ind:
            n = mapblks[i]
            if p == 0:
                sortedAndMergedBlks.append(mapblks[i])
            else:
                if n["ls"] <= p["le"]:
                    print("merged")
                    p["le"] = max(n["le"],p["le"])
                else:
                    sortedAndMergedBlks.append(mapblks[i])
            p = n

        print("file: ",file)
        print("total_clusters: ",blks)
        print("cluster_size_b: ",blksize)
        print("total_size_b: ",blks*blksize)
        print("extent_count: ",len(sortedAndMergedBlks))
        print("extents:")
        for i in sortedAndMergedBlks:
            print(" - {{lcn: [{},{}], vcn: [{},{}]}}".format(i["ls"],i["le"],i["vs"],i["ve"]))




        
parser = argparse.ArgumentParser(
                    prog='XFS sorted frag',
                    description='Sorted frag',
                    epilog='Pass a file')
parser.add_argument('-f','--file', required=True)
args = parser.parse_args()
analyzeFile(args.file)

