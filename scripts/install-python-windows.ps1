<#
PowerShell helper to install Python on Windows.

This script attempts to install Python using winget if available, otherwise
it downloads the official installer and runs it interactively.

Run in an elevated PowerShell prompt for a system-wide install.
#>
try {
    $ErrorActionPreference = 'Stop'
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host 'Installing Python via winget...'
        winget install --id Python.Python.3 -e --source winget
        Write-Host 'Python install requested via winget. You may need to restart the shell.'
        exit 0
    } else {
        Write-Host 'winget not available, downloading official installer...'
        $tmp = "$env:TEMP\python-installer.exe"
        $url = 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe'
        Invoke-WebRequest -Uri $url -OutFile $tmp
        Write-Host 'Running the installer (interactive). Check the "Add Python to PATH" box.'
        Start-Process -FilePath $tmp -Wait
        Remove-Item $tmp -Force
        Write-Host 'Installer finished. Open a new PowerShell session to pick up PATH changes.'
        exit 0
    }
} catch {
    Write-Error "Python installation helper failed: $_"
    exit 1
}
