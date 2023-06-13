$filefrag = "R:\w32filefrag.exe"
$sfanalyze = "R:\sortedfrag-analyze.ps1"

$folder= "R:\r1\Backup Job 4"
$cachefolder = "R:\sfcache"

#block size, if you have been a good admin, you formated refs with 64 blocksize
$b = 65536

$cpath = Join-Path $cachefolder (Get-Item -Path $folder).BaseName
New-Item -ItemType Directory $cpath -ErrorAction SilentlyContinue  | Out-Null

foreach($f in (Get-ChildItem $folder | ? { $_.name -match ".(vbk|vib)$" })) {
 . $filefrag "-o" ("""{0}\{1}.frag""" -f $cpath,$f.BaseName) ("""{0}""" -f $f.fullname) 
}


. $sfanalyze -dirs $cpath -b 65536
