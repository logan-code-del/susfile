$envFilePath = ".\new.env"

# Check if the .env file exists
if (Test-Path $envFilePath) {
    # Read each line of the .env file
    Get-Content $envFilePath | ForEach-Object {
        # Skip empty lines or lines starting with a hash (#) as they are comments
        if (-not ([string]::IsNullOrWhiteSpace($_)) -and -not $_.TrimStart().StartsWith("#")) {
            # Split the line by the first '=' to separate variable name and value
            $parts = $_.Split('=', 2)
            if ($parts.Count -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()

                # Set the environment variable in the current PowerShell session
                # This makes it accessible using $env:VariableName
                Set-Item -Path Env:$name -Value $value
            }
        }
    }
} else {
    Write-Warning "'.env' file not found at $envFilePath."
}


.\scripts\win-launcher.ps1 -Dest "$env:USERPROFILE\susfile-run" -InstallNode -UsePythonViewer -CreateIssue -Cleanup -SecretsRepo 'logan-code-del/secrets-repo'