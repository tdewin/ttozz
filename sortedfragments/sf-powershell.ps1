$filefrag = "R:\w32filefrag.exe"
$python = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
$sfanalyze = "R:\sortedfrag-analyze.py"

$folder= "R:\r1\Backup Job 4"
$cachefolder = "R:\sfcache"

#block size, if you have been a good admin, you formated refs with 64 blocksize
$b = 65536

$cpath = Join-Path $cachefolder (Get-Item -Path $folder).BaseName
New-Item -ItemType Directory $cpath -ErrorAction SilentlyContinue  | Out-Null

foreach($f in (Get-ChildItem $folder | ? { $_.name -match ".(vbk|vib)$" })) {
 . $filefrag $f.fullname | Set-Content -Encoding UTF8 (Join-Path $cpath ("{0}.frag" -f $f.BaseName))
}


. $python $sfanalyze  -d $cpath -b 65536

