# XFS accounting for ref link

Initially ttozz uses a process of fingerprinting the blocks in each interval. This did not yield good result. It seems xfs_bmap does not report on all blocks and ironically filefrag does (or it aligns better with ls output). Go to ttozz folder for legacy reference

Sortedfragments is a two stage process. 
- Use sortedfrag.py to create a frag file. This is basically filefrag output but reordered on volume level offset instead of file level offset making the list ready to compare multiple files.
- Use sortedfrag-analyze.py to get statistics on these files. 
Look at at sf-sample.sh to see how these would work together

The reason to split it up is that ordening blocks is resource intensive but unless you defragment your filesystem or modify your files does not have to recreated on each and every run. Rather fragments should remain quite static for one file. Thus once start, you should only use sortedfray.py on new files. 

Additionally the output is https://github.com/tdewin/w32filefrag , so you should be able to use sortedfrag-analyze.(py|ps1) to analyze ReFS frags created with w32filefrag. sf-sample.ps1 is provided for such a setup.