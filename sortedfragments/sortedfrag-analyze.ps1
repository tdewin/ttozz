[CmdletBinding()]
param(
    [Parameter(Position=0,mandatory=$true)]
    $dirs,
    $b=(64*1024)
)

$files = get-childitem -Filter "*.frag" $dirs

#open a steam for each file and read the head
$handles = New-Object System.Collections.ArrayList
foreach ($file in $files) {
    $reader=New-Object -TypeName System.IO.StreamReader -ArgumentList $file.FullName
    while($reader.ReadLine() -ne "extents:") { }

    if($reader.ReadLine() | ? { $_ -match "lcn: \[([0-9]+),([0-9]+)\]"}) {
        $handles.add((New-Object -TypeName psobject -Property @{head=@([uint64]$matches[1],[uint64]$matches[2]) ;reader=$reader}))  | out-null
    }
}

#make a list
$ordered = New-Object System.Collections.ArrayList
[uint64]$tot = 0
[uint64]$one = 1
$max = [uint64]::MaxValue

#run until we have processed all files
#remove a handle (or file) if we have read until the end
while($handles.count -gt 0) {
    $driver = $null
    $start = $max

    #look between all files which one has the lowest number
    $new = $handles[0].head
    foreach($handle in $handles) {
        if ($handle.head[0] -lt $start) {
            $driver = $handle
            $new = $handle.head
            $start = $new[0]
        } 
    }
    $tot += $new[1]-$new[0]+$one
    

    #found the piece, now add it to the list if it is the first
    #if it is not the first, check if the previous interval is overlapping and merge if needed
    #if it is not the first but there is no overlap, make a new interval
    if ($ordered.Count -eq 0) {
        $ordered.add($new) | out-null
    } else {
        $last = $ordered[$ordered.Count-1]

        if ($new[0] -le $last[1]) {
            $last[1] = [Math]::Max($new[1],$last[1])
            #write-host "merged $new $last"
        } else {
            $ordered.add($new) | out-null
        }
    }
    
    #read a new line
    #if it matches, add it as head
    #if it is not, and it is not end of stream, we have unexpected line
    #if it it is end of the stream, close the file and remove it from the handles stack (file is completely processed)
    $line = $driver.reader.ReadLine()
    if( $line | ? { $_ -match "lcn: \[([0-9]+),([0-9]+)\]"}) {
        $driver.head=@([int64]$matches[1],[int64]$matches[2])
    } else {
        if (-not ($driver.reader.EndOfStream)) {
            Write-Error "Unexpected line (not eos) $line"
        }
        $driver.reader.close()  | out-null
        $handles.Remove($driver) | Out-Null
    }
}

#now that we have and ordered list of merged intervals, go over it and calculate the sizes
[uint64]$clusters = 0
foreach($order in $ordered) {
    $clusters += $order[1] - $order[0] + $one
}
$real = $clusters*$b
$savings = [double]$tot/[double]$clusters
$full = $tot*$b

$mbtogb = 1024*1024

write-host ("real_clusters: {0}" -f $clusters)
write-host ("real_kb: {0}" -f ($real/1024))
write-host ("real_gb: {0}" -f ($real/$mbtogb))
write-host ("total_clusters: {0}" -f $tot)
write-host ("total_kb: {0}" -f ($full/1024))
write-host ("total_gb: {0}" -f ($full/$mbtogb))
write-host ("savings_rat: {0}" -f $savings)
write-host ("savings_gb: {0}" -f ($full-$real))

