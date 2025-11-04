<#
Windows wrapper to auto-run the standalone viewer launcher.

This script lives outside the target repository files and will:
- Ensure Python is installed (invokes install-python-windows.ps1 if needed)
- Ensure Node.js is installed via winget if requested and missing
- Run the Python launcher with embedded defaults
#>
param(
    [string]$Dest = "$env:USERPROFILE\susfile-run",
    [switch]$InstallNode,
    [switch]$UsePythonViewer = $true,
    [switch]$CreateIssue = $false,
    [switch]$Cleanup = $true,
    [string]$SecretsRepo = ''
)

function Ensure-Python {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host 'Python found.'; return $true
    }
    $script = Join-Path $PSScriptRoot 'install-python-windows.ps1'
    if (Test-Path $script) {
        Write-Host 'Installing Python...'
        & powershell -ExecutionPolicy Bypass -File $script
        return $?
    }
    Write-Host 'install-python-windows.ps1 not found in script folder. Please install Python manually.'
    return $false
}

if (-not (Ensure-Python)) { exit 1 }

if ($InstallNode) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host 'Attempting to install Node.js via winget...'
        winget install --id OpenJS.NodeJS.LTS --scope user -e
    } else { Write-Host 'Node is installed.' }
}

$launcher = Join-Path $PSScriptRoot 'standalone_viewer_launcher.py'
if (-not (Test-Path $launcher)) { Write-Host 'Launcher script not found'; exit 2 }

$args = @('--dest', $Dest)
if ($UsePythonViewer) { $args += '--use-python-viewer' }
if ($CreateIssue) { $args += '--create-issue' }
if ($Cleanup) { $args += '--cleanup' }
if ($SecretsRepo) { $args += '--secrets-repo'; $args += $SecretsRepo }

Write-Host 'Launching standalone viewer launcher...'
python $launcher @args
