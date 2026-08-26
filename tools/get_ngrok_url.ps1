$publicUrl = $null
for ($i = 0; $i -lt 30 -and -not $publicUrl; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri http://127.0.0.1:4040/api/tunnels -ErrorAction Stop
        if ($resp.tunnels.Count -gt 0) {
            $publicUrl = $resp.tunnels[0].public_url
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 1
}
if ($publicUrl) {
    Write-Output $publicUrl
} else {
    Write-Output "NGROK_URL_NOT_FOUND"
}