$ProjectPath = $PSScriptRoot
$DataDir     = Join-Path $ProjectPath "dat"
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

$PythonExe   = Join-Path $ProjectPath "venv\Scripts\python.exe"
$BotScript   = Join-Path $ProjectPath "bot.py"
$LogFile     = Join-Path $DataDir "watchdog.log"
$WatchdogPidFile = Join-Path $DataDir "watchdog.pid"
$BotPidFile      = Join-Path $DataDir "bot.pid"

$MinUptimeSeconds = 60
$RestartDelaySeconds = 5

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

if (Test-Path $WatchdogPidFile) {
    $existingPid = Get-Content $WatchdogPidFile -ErrorAction SilentlyContinue
    if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
        Write-Log "Ya hay un watchdog corriendo (PID $existingPid). No se inicia uno nuevo."
        exit 1
    }
}

if (-not (Test-Path $PythonExe)) {
    Write-Log "ERROR FATAL: No se encontro python.exe del venv en $PythonExe"
    exit 1
}
if (-not (Test-Path $BotScript)) {
    Write-Log "ERROR FATAL: No se encontro bot.py en $BotScript"
    exit 1
}

$PID | Out-File -FilePath $WatchdogPidFile -Encoding ascii -Force

$currentProcess = $null

try {
    Write-Log "Watchdog iniciado (PID $PID). Proyecto: $ProjectPath"

    while ($true) {
        Write-Log "Iniciando bot (python.exe del venv, sin ventana visible)..."
        $startTime = Get-Date

        $currentProcess = Start-Process -FilePath $PythonExe `
            -ArgumentList "`"$BotScript`"" `
            -WorkingDirectory $ProjectPath `
            -WindowStyle Hidden `
            -PassThru

        $currentProcess.Id | Out-File -FilePath $BotPidFile -Encoding ascii -Force
        Write-Log "Bot iniciado (PID $($currentProcess.Id))."

        while (-not $currentProcess.HasExited) {
            Start-Sleep -Milliseconds 500
        }

        $uptime = ((Get-Date) - $startTime).TotalSeconds
        $exitCode = $currentProcess.ExitCode
        Write-Log "El bot se detuvo (PID $($currentProcess.Id)). Codigo de salida: $exitCode. Tiempo activo: $([math]::Round($uptime,1)) segundos."

        if ($uptime -lt $MinUptimeSeconds) {
            Write-Log "El bot se cerro antes de $MinUptimeSeconds segundos. Se asume error de inicio. Watchdog detenido para evitar bucle infinito."
            break
        }

        Write-Log "El bot estuvo activo mas de $MinUptimeSeconds segundos. Reiniciando en $RestartDelaySeconds segundos..."
        Start-Sleep -Seconds $RestartDelaySeconds
    }
}
finally {
    if ($currentProcess -and -not $currentProcess.HasExited) {
        Write-Log "Cerrando proceso del bot (PID $($currentProcess.Id)) por finalizacion del watchdog..."
        Stop-Process -Id $currentProcess.Id -Force -ErrorAction SilentlyContinue
    }
    Remove-Item $WatchdogPidFile -Force -ErrorAction SilentlyContinue
    Remove-Item $BotPidFile -Force -ErrorAction SilentlyContinue
    Write-Log "Watchdog finalizado."
}