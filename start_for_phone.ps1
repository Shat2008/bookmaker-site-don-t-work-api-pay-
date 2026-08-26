# Start Django development server and ngrok (PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File .\start_for_phone.ps1

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

# Start Django dev server in background
Write-Host "Starting Django dev server on 0.0.0.0:8000..."
Start-Process -FilePath $pythonCmd.Source -ArgumentList "manage.py","runserver","0.0.0.0:8000"
Start-Sleep -Seconds 2

# Try to find ngrok
$ngrokCmd = Get-Command ngrok -ErrorAction SilentlyContinue
if ($ngrokCmd) {
    Write-Host "ngrok found - starting tunnel on port 8000..."
    Start-Process -FilePath $ngrokCmd.Source -ArgumentList "http","8000"

    # Try to obtain public URL from local ngrok API
    $publicUrl = $null
    $attempts = 0
    while ($attempts -lt 15 -and -not $publicUrl) {
        try {
            $resp = Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels -ErrorAction Stop
            if ($resp.tunnels.Count -gt 0) {
                $publicUrl = $resp.tunnels[0].public_url
                break
            }
        } catch {
            # ngrok may not be ready yet
        }
        Start-Sleep -Seconds 1
        $attempts++
    }

    if ($publicUrl) {
        Write-Host "Open this URL on your phone: $publicUrl"
    } else {
        Write-Host "Could not automatically retrieve ngrok URL. Open the ngrok console and copy the URL manually."
    }
} else {
    Write-Host "ngrok not found in PATH. The script started only the dev server. To make the site reachable from your phone, install ngrok or cloudflared and run a tunnel."
    Write-Host "Manual example: ngrok http 8000"
}

Write-Host "To stop the server - close windows/stop processes or press Ctrl+C in the server window." 
Pop-Location
