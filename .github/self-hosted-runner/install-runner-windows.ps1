<#
install-runner-windows.ps1

Usage (PowerShell):
  $env:GITHUB_URL = 'https://github.com/owner/repo'
  $env:RUNNER_TOKEN = '<registration token>'
  $env:RUNNER_NAME = 'susfile-windows-runner'
  $env:RUNNER_LABELS = 'self-hosted,viewer'
  .\install-runner-windows.ps1

This script downloads the Actions Runner for Windows, configures it with the
provided registration token, and launches it interactively (run.cmd).

#>
param()

Set-StrictMode -Version Latest

$githubUrl = $env:GITHUB_URL
if (-not $githubUrl) { Write-Error 'GITHUB_URL environment variable is required'; exit 1 }

$token = $env:RUNNER_TOKEN
if (-not $token) { Write-Error 'RUNNER_TOKEN environment variable is required (short-lived registration token)'; exit 1 }

$runnerName = $env:RUNNER_NAME; if (-not $runnerName) { $runnerName = 'susfile-windows-runner' }
$runnerLabels = $env:RUNNER_LABELS; if (-not $runnerLabels) { $runnerLabels = 'self-hosted,viewer' }
$runnerVersion = $env:RUNNER_VERSION; if (-not $runnerVersion) { $runnerVersion = '2.308.0' }

$archive = "actions-runner-win-x64-$runnerVersion.zip"
$url = "https://github.com/actions/runner/releases/download/v$runnerVersion/$archive"

Write-Host "Downloading runner $runnerVersion..."
$outDir = Join-Path $PSScriptRoot 'actions-runner'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

$zipPath = Join-Path $outDir $archive
Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

Write-Host 'Extracting...'
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $outDir)

Set-Location $outDir

Write-Host 'Configuring runner (unattended)...'
.\\config.cmd --url $githubUrl --token $token --name $runnerName --labels $runnerLabels --unattended

Write-Host 'Starting runner interactively. Close this window to stop the runner.'
Start-Process -FilePath '.\run.cmd' -NoNewWindow -Wait
