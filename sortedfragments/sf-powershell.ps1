$filefrag = "R:\r1\w32filefrag.exe"
$python = "C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"

#block size, if you have been a good admin, you formated refs with 64 blocksize
$b = 65536


[System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null

$foldername = New-Object System.Windows.Forms.FolderBrowserDialog
$foldername.rootfolder = "MyComputer"
$foldername.ShowDialog()

$folder = $foldername.SelectedPath
$files = Get-ChildItem $folder | ? { $_.name -match ".(vbk|vib)$" }



foreach($f in $files) {
 . $filefrag $f.fullname | Set-Content -Encoding UTF8 ("{0}.frag" -f $f.BaseName)
}


 sortedfrag-analyze.py -d "Backup Job 4" -b 65536