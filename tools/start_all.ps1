# Start both Django dev server and ngrok tunnel and print public URL
# Usage: powershell -ExecutionPolicy Bypass -File .\tools\start_all.ps1

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot

Write-Host "Working directory: $projectRoot"

# Locate python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python not found in PATH. Install Python and add it to PATH."
    Pop-Location
    exit 1
}

# Start Django dev server bound to 127.0.0.1:8000
Write-Host "Starting Django dev server on 127.0.0.1:8000..."
$pythonPath = $pythonCmd.Source
Start-Process -FilePath $pythonPath -ArgumentList @('manage.py','runserver','127.0.0.1:8000') -WindowStyle Minimized | Out-Null
Start-Sleep -Seconds 2

# Find ngrok (check tools/ngrok first, then PATH)
$ngrokPath = $null
$localNgrok = Join-Path $projectRoot 'tools\ngrok\ngrok.exe'
if (Test-Path $localNgrok) { $ngrokPath = $localNgrok } else { $ngrokCmd = Get-Command ngrok -ErrorAction SilentlyContinue; if ($ngrokCmd) { $ngrokPath = $ngrokCmd.Source } }

if (-not $ngrokPath) {
    Write-Host 'ngrok not found. Place ngrok.exe into tools\ngrok or add ngrok to PATH.'
    Pop-Location
    exit 1
}

Write-Host "Starting ngrok from: $ngrokPath (target: 127.0.0.1:8000)"
Start-Process -FilePath $ngrokPath -ArgumentList @('http','127.0.0.1:8000') -WindowStyle Minimized | Out-Null

# Poll local ngrok API for public URL
$publicUrl = $null
$attempts = 0
while ($attempts -lt 30 -and -not $publicUrl) {
    try {
        $resp = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -ErrorAction Stop
        if ($resp.tunnels -and $resp.tunnels.Count -gt 0) { $publicUrl = $resp.tunnels[0].public_url; break }
    } catch {
        # ngrok not ready yet
    }
    Start-Sleep -Seconds 1
    $attempts++
}

if ($publicUrl) {
    Write-Host "NGROK_PUBLIC_URL: $publicUrl"
    Write-Host 'Open this URL on your phone.'
} else {
    Write-Host 'Could not retrieve ngrok public URL. Run ngrok manually: ngrok http 127.0.0.1:8000'
}

Pop-Location
