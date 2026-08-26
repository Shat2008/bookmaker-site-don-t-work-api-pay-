$ErrorActionPreference = 'Stop'
$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'manage.py' }
if ($procs) {
    foreach ($p in $procs) {
        Write-Output ("Killing PID: $($p.ProcessId)")
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Output 'No manage.py processes found'
}
