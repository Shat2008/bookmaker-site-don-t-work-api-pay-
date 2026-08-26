<#
Interactive helper to switch the project to live Stripe keys.
Runs locally and updates .env (creates a backup .env.bak).
You will be prompted to paste secrets — they are never sent anywhere.
#>

param ()
$ErrorActionPreference = 'Stop'
$cwd = Get-Location
$envFile = Join-Path $cwd '.env'
$backup = Join-Path $cwd '.env.bak'
if (Test-Path $envFile) {
    Copy-Item $envFile $backup -Force
    Write-Host "Backed up existing .env to .env.bak"
} else {
    Write-Host "No .env found — creating new one"
}

# Read current .env into a hashtable
$lines = @{}
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*#') { return }
        if ($_ -match '^\s*$') { return }
        $parts = $_ -split '='
        $key = $parts[0].Trim()
        $val = ($parts[1..($parts.Length-1)] -join '=').Trim()
        $lines[$key] = $val
    }
}

function Read-Secret([string]$prompt, [bool]$allowEmpty=$false) {
    while ($true) {
        $v = Read-Host $prompt
        if ($v -or $allowEmpty) { return $v }
        Write-Host "Value cannot be empty, please paste the value."
    }
}

Write-Host "--- Switch to LIVE Stripe mode helper ---"
$livePublic = Read-Host 'Paste STRIPE_PUBLIC_KEY (pk_live_...) or leave empty to keep existing'
$liveSecret = Read-Host 'Paste STRIPE_SECRET_KEY (sk_live_...) or leave empty to keep existing'
$liveWebhook = Read-Host 'Paste STRIPE_WEBHOOK_SECRET (whsec_...) or leave empty to keep existing'
$siteUrl = Read-Host "Paste SITE_URL (https://your-domain.example) — ngrok temporary URL OK"

# Update hashtable
if ($livePublic) { $lines['STRIPE_PUBLIC_KEY'] = $livePublic }
if ($liveSecret) { $lines['STRIPE_SECRET_KEY'] = $liveSecret }
if ($liveWebhook) { $lines['STRIPE_WEBHOOK_SECRET'] = $liveWebhook }
if ($siteUrl) { $lines['SITE_URL'] = $siteUrl.TrimEnd('/') ; $lines['ALLOWED_HOSTS'] = $lines['ALLOWED_HOSTS'] -replace '\s*', '' ; $lines['ALLOWED_HOSTS'] = "$($lines['ALLOWED_HOSTS']),$($siteUrl -replace 'https?://','')" }

# Set DEBUG=False
$lines['DEBUG'] = 'False'

# Write back .env
$out = @()
# Preserve some common keys ordering
$orderedKeys = @('SECRET_KEY','DEBUG','ALLOWED_HOSTS','SITE_URL','STRIPE_PUBLIC_KEY','STRIPE_SECRET_KEY','STRIPE_WEBHOOK_SECRET')
foreach ($k in $orderedKeys) {
    if ($lines.ContainsKey($k)) { $out += "$k=$($lines[$k])" ; $lines.Remove($k) }
}
foreach ($k in $lines.Keys) { $out += "$k=$($lines[$k])" }
$out | Set-Content -Path $envFile -Encoding UTF8
Write-Host "Updated .env — DEBUG=False and keys set (where provided). Backup is at .env.bak"

# Restart server using start_for_phone.ps1
$startScript = Join-Path $cwd 'start_for_phone.ps1'
if (Test-Path $startScript) {
    Write-Host "Restarting dev server to apply changes..."
    # Kill manage.py processes first
    & powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\kill_manage.ps1
    Start-Sleep -Seconds 1
    & powershell -NoProfile -ExecutionPolicy Bypass -File .\start_for_phone.ps1
    Write-Host "Server restarted."
} else {
    Write-Host "start_for_phone.ps1 not found — please restart your server manually."
}

Write-Host "IMPORTANT: For production real-money usage, deploy to a secure HTTPS host and verify Stripe webhook secret for the live account."
