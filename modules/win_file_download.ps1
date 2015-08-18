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

Function download_file ($source, $destination){
 # TODO: do try catch error
  $webclient = New-Object System.Net.WebClient
  
  
  Try {
    $webclient.DownloadFile($source,$destination)
    $result.changed = $true
  }
  
  Catch {
    Fail-Json $result "Error downloading $src"
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

# Source check: First we create the request.
$HTTP_Request = [System.Net.WebRequest]::Create('http://google.com')
  
# We then get a response from the site.
$HTTP_Response = $HTTP_Request.GetResponse()

# We then get the HTTP code as an integer.
$HTTP_Status = [int]$HTTP_Response.StatusCode


# src check
If ($HTTP_Status -ne 200){
  # // File does not exist or site in N/A
  Fail-Json $result "The source file $src does not exist"
}

# we clean up the http request by closing it.
$HTTP_Response.Close()

# dest check
If (Test-Path $dest){
  # // File does exist 
  if ($force){
    download_file $src $dest   
  }

  Else{
    Exit-Json $result;     
  }
}
Else {
  download_file $src $dest
}


$result.msg = $item_src


Exit-Json $result;