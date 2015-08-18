#!powershell

# WANT_JSON
# POWERSHELL_COMMON

## parm src (man) dest(man) force(default false)

## if src doest exists
##  fail

## if dest exits
##  if dest == fs dest
##      do nothing we are good [changed = False]
##  else
##      if force == false
##          fail
##      else
##          rm fs dest 
##          call create link
## else
##      call create link 

## function create
##   [changed = True ]
##   fail maybe



$params = Parse-Args $args;

$result = New-Object psobject @{
    win_file_lnk = New-Object psobject
    changed = $false
}

Function copy_file ($source, $destination){
 # TODO: do try catch error
  
  Try {
    Copy-Item -Path $src -Destination $dest
    $result.changed = $true
  }
  
  Catch {
    Fail-Json $result "Error copying $src to $dest"
  }

}


# Parm checks
If ($params.src) {
    $src = $params.src
}
Else {
    Fail-Json $result "missing required argument: src"
}
If ($params.dest) {
    $dest = $params.dest
}
Else {
    Fail-Json $result "missing required argument: dest"
}
If ($params.force) {
    # TODO: only accepts boolean arg else fail
    $force = $params.force
}
Else {
    $force = $false
}

# src check
If (!(Test-Path $src)){
  # // File does not exist
  Fail-Json $result "The source file $src does not exist"
}

# dest check
If (Test-Path $dest){
  # // File does exist
  
  if ($force){
    copy_file $src $dest   
  }
  Else{
    Exit-Json $result;     
  }


}
Else {
  copy_file $src $dest
}


$result.msg = $item_src


Exit-Json $result;