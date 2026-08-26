# Check parsing of start_all.ps1
$s = Get-Content "$PSScriptRoot\start_all.ps1" -Raw
try {
    [System.Management.Automation.Language.Parser]::ParseInput($s, [ref]$null, [ref]$null)
    Write-Host 'PARSE_OK'
} catch {
    Write-Host 'PARSE_ERROR:' $_.Exception.Message
    exit 1
}
