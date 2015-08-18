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

Function create_lnk ($source, $destination){
 # TODO: do try catch error
  $WshShell = New-Object -comObject WScript.Shell
  $Shortcut = $WshShell.CreateShortcut("$destination")
  $Shortcut.TargetPath = "$source"
  
  Try {
    $Shortcut.Save()
    $result.changed = $true
  }
  
  Catch {
    Fail-Json $result "Error creating a shortcut of $src"
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
  $sh = New-Object -COM WScript.Shell
  $targetPath = $sh.CreateShortcut($dest).TargetPath
  if ($TargetPath -eq $src){
    Exit-Json $result;
  }
  Elseif ($force){
    create_lnk $src $dest   
  }
  Else{
    Fail-Json $result "The destination shortcut $dest does exist and force = false!"     
  }


}
Else {
  create_lnk $src $dest
}


$result.msg = $item_src


Exit-Json $result;