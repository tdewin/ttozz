$filefrag = "R:\w32filefrag.exe"
$python = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
$sfanalyze = "R:\sortedfrag-analyze.py"
$cachefolder = "R:\sfcache"

#block size, if you have been a good admin, you formated refs with 64 blocksize
$b = 65536


New-Item -ItemType Directory $cachefolder -ErrorAction SilentlyContinue | Out-Null

[System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null

$foldername = New-Object System.Windows.Forms.FolderBrowserDialog
$foldername.rootfolder = "MyComputer"
$foldername.ShowDialog()

$folder = $foldername.SelectedPath
$files = Get-ChildItem $folder | ? { $_.name -match ".(vbk|vib)$" }

$cpath = Join-Path $cachefolder (Get-Item -Path $folder).BaseName
New-Item -ItemType Directory $cpath -ErrorAction SilentlyContinue  | Out-Null

foreach($f in $files) {
 . $filefrag $f.fullname | Set-Content -Encoding UTF8 (Join-Path $cpath ("{0}.frag" -f $f.BaseName))
}


. $python $sfanalyze  -d $cpath -b 65536

read-host