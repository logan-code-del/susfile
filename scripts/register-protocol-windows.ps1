<#
Register a custom URL protocol `susviewer://` for the current user which will
launch the `win-launcher.ps1` script located in the same folder as this script.

Run this in PowerShell (no elevation required for HKCU):
  powershell -ExecutionPolicy Bypass -File .\scripts\register-protocol-windows.ps1

To unregister, run the same script with -Unregister switch.
#>

param(
    [switch]$Unregister
)

function Get-ScriptFolder {
    $Invocation = (Get-Variable MyInvocation -Scope 1).Value
    Split-Path -Parent $Invocation.MyCommand.Definition
}

$folder = Get-ScriptFolder
$protocol = 'susviewer'
$keyPath = "HKCU:\Software\Classes\$protocol"

if ($Unregister) {
    if (Test-Path $keyPath) {
        Remove-Item -Path $keyPath -Recurse -Force
        Write-Host "Unregistered protocol $protocol"
    } else {
        Write-Host "Protocol $protocol is not registered"
    }
    exit 0
}

$launcher = Join-Path $folder 'win-launcher.ps1'
if (-not (Test-Path $launcher)) {
    Write-Error "Could not find win-launcher.ps1 in $folder. Copy register-protocol-windows.ps1 into the scripts folder and run it there."
    exit 2
}

$command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$launcher`" "%1""

Write-Host "Registering protocol $protocol to run: $command"

New-Item -Path $keyPath -Force | Out-Null
New-ItemProperty -Path $keyPath -Name '(Default)' -Value 'URL: susviewer Protocol' -Force | Out-Null
New-ItemProperty -Path $keyPath -Name 'URL Protocol' -Value '' -Force | Out-Null

New-Item -Path (Join-Path $keyPath 'DefaultIcon') -Force | Out-Null
New-ItemProperty -Path (Join-Path $keyPath 'DefaultIcon') -Name '(Default)' -Value "$launcher,0" -Force | Out-Null

New-Item -Path (Join-Path $keyPath 'shell\open\command') -Force | Out-Null
New-ItemProperty -Path (Join-Path $keyPath 'shell\open\command') -Name '(Default)' -Value $command -Force | Out-Null

Write-Host "Protocol registered. You can test by opening: susviewer://launch in your browser or Run dialog (Win+R)."
Write-Host "To unregister: run this script with -Unregister"
