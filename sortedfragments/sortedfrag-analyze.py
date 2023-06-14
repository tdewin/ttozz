#!/usr/bin/python3

import argparse
import re
import glob
import math

def parseLine(ln):
    res = None
    m = re.search("{lcn:\s*\[\s*([0-9]+)\s*,\s*([0-9]+)\s*\],\s*vcn",ln)
    if m:
        res = [int(m.group(1)),int(m.group(2))]

    return res


def analyzeDir(idir,blksize):
    gpattern = idir+"/*.frag"
    files = glob.glob(gpattern)   

    stacks = {}
    for f in files:
        reader = open(f, 'r')
        while reader.readline().strip() != "extents:":
            #skip
            pass
        m = parseLine(reader.readline())
        if m != None:
            stacks[f] = {"reader":reader,"head":m}
        else:
            print("Trouble seeking and finding first extend for",f)

    real = 0
    total = 0
    working = [-1,-2]
    accounted = True

    while len(stacks) > 0:
        c = None
        cname = None
        i = math.inf

        for s in stacks:
            n = stacks[s]
            t = n["head"][0]
            if t < i:
                i = t
                c = n
                cname = s
        
        current = c["head"]
        
        #reported by all files
        #interval 0..0 is 1
        total += (current[1]-current[0])+1

        if current[0] <= working[1]:
            if working[0] <= current[0]:
                working[1] = max(current[1],working[1])
            else:
                print("not sorted list detected")
        else:
            #interval 0..0 is 1
            real += (working[1]-working[0])+1
            working = current
        

        ln = c["reader"].readline()
        if ln:
            m = parseLine(ln)
            if m:
                c["head"] = m
            else:
                print("Read a line for",c,"but it didnt confirm.",ln)
        else:
            c["reader"].close()
            print("End of",cname)
            stacks.pop(cname)

    #add last interval
    #interval 0..0 is 1
    real += (working[1]-working[0])+1
   
    savings_rat = total/real

    blkkb = blksize/1024
    #blksize is in kb
    rkb = int(real*(blkkb))
    tkb = int(total*(blkkb))

    #(>>17)/8 is like dividing by 2^20 or kb to gb
    # (int(math.pow(2,20)) >> 17)/8 = 1
    print("real_clusters: ",real)
    print("real_kb: ",rkb)
    print("real_gb: ",(rkb>>16)/16)
    print("total_clusters: ",total)
    print("total_kb: ",tkb)
    print("total_gb: ",(tkb>>16)/16)
    print("savings_rat: ",savings_rat)
    print("savings_gb:",(((tkb-rkb)>>16)/16))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='XFS sorted frag analyze',
                    description='Sorted frag',
                    epilog='Pass a the directory with frag files')
    parser.add_argument('-d','--dir', required=True)
    parser.add_argument('-b','--blksize', default=4096,type=int)
    args = parser.parse_args()
    analyzeDir(args.dir,args.blksize)

