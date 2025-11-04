$emv:GITHUB_TOKEN = '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'

.\scripts\win-launcher.ps1 -Dest "$env:USERPROFILE\susfile-run" -InstallNode -UsePythonViewer -CreateIssue -Cleanup -SecretsRepo 'logan-code-del/secrets-repo'