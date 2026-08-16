$ProjectPath = $PSScriptRoot
$DataDir     = Join-Path $ProjectPath "dat"

$LogFile = Join-Path $DataDir "watchdog.log"
$WatchdogPidFile = Join-Path $DataDir "watchdog.pid"
$BotPidFile = Join-Path $DataDir "bot.pid"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

Write-Log "Detencion manual solicitada via detener_bot.bat"
$stopped = $false

if (Test-Path $WatchdogPidFile) {
    $wpid = Get-Content $WatchdogPidFile -ErrorAction SilentlyContinue
    if ($wpid -and (Get-Process -Id $wpid -ErrorAction SilentlyContinue)) {
        Write-Log "Cerrando watchdog PID $wpid"
        Stop-Process -Id $wpid -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
}

if (Test-Path $BotPidFile) {
    $bpid = Get-Content $BotPidFile -ErrorAction SilentlyContinue
    if ($bpid -and (Get-Process -Id $bpid -ErrorAction SilentlyContinue)) {
        Write-Log "Cerrando bot PID $bpid"
        Stop-Process -Id $bpid -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
}

$residuales = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*watchdog.ps1*" -or $_.CommandLine -like "*bot.py*"
}
foreach ($proc in $residuales) {
    Write-Log "Cerrando proceso residual PID $($proc.ProcessId)"
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    $stopped = $true
}

Remove-Item $WatchdogPidFile -Force -ErrorAction SilentlyContinue
Remove-Item $BotPidFile -Force -ErrorAction SilentlyContinue

if (-not $stopped) {
    Write-Log "No se encontro ningun proceso activo al ejecutar detener_bot.bat"
    Write-Host "No se encontro ningun proceso activo."
}
Write-Log "detener_bot.bat finalizo."

Write-Host ""
Write-Host "Listo. Revisa Discord para confirmar que el bot quedo desconectado."
Read-Host "Presiona Enter para cerrar"