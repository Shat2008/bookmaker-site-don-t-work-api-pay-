$ErrorActionPreference = 'Stop'
$rel = Invoke-RestMethod -UseBasicParsing 'https://api.github.com/repos/stripe/stripe-cli/releases/latest'
$asset = $rel.assets | Where-Object { $_.name -match 'windows' -and ($_.name -match 'amd64' -or $_.name -match 'x86_64') } | Select-Object -First 1
if (-not $asset) { Write-Output 'NO_WINDOWS_ASSET'; exit 1 }
$url = $asset.browser_download_url
New-Item -ItemType Directory -Force -Path tools | Out-Null
$zip = Join-Path $PWD 'tools\stripe_latest.zip'
Write-Output ("Downloading $url to $zip")
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath (Join-Path $PWD 'tools\stripe') -Force
$exe = Get-ChildItem -Path (Join-Path $PWD 'tools\stripe') -Recurse -Filter 'stripe.exe' | Select-Object -First 1
if ($exe) { Write-Output ('DOWNLOADED_AT:' + $exe.FullName) } else { Write-Output 'EXE_NOT_FOUND' }
