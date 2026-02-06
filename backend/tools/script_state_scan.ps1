# tools/script_state_scan.ps1
# Purpose: Scan SCRIPT_STATE_REGISTRY.json and report script states

$ErrorActionPreference = "Stop"

$repoRoot = Get-Location
$registryPath = Join-Path $repoRoot "docs\SCRIPT_STATE_REGISTRY.json"
$outputDir = Join-Path $repoRoot "evidence\audits"
$outputFile = Join-Path $outputDir "script_state_scan_latest.txt"

# Ensure output directory exists
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Check if registry exists
if (!(Test-Path $registryPath)) {
    Write-Host "[FAIL] Registry not found: $registryPath" -ForegroundColor Red
    exit 1
}

# Parse JSON registry
$registryContent = Get-Content $registryPath -Raw
$registry = $registryContent | ConvertFrom-Json
$files = @{}

foreach ($fileKey in $registry.files.PSObject.Properties.Name) {
    $fileData = $registry.files.$fileKey
    $files[$fileKey] = @{
        state   = if ($fileData.state) { $fileData.state } else { "OBSERVE" }
        settled = if ($null -ne $fileData.settled) { $fileData.settled } else { $false }
        reason  = if ($fileData.reason) { $fileData.reason } else { "" }
    }
}

# Group by state
$frozen = @()
$stable = @()
$repair = @()
$observe = @()

foreach ($file in $files.Keys) {
    $state = $files[$file].state
    switch ($state) {
        "FROZEN" { $frozen += $file }
        "STABLE" { $stable += $file }
        "REPAIR" { $repair += $file }
        "OBSERVE" { $observe += $file }
        default { $observe += $file }
    }
}

# Build report
$report = @()
$report += "SCRIPT STATE SCAN REPORT"
$report += "=" * 60
$report += "Timestamp: $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
$report += "Registry: $registryPath"
$report += "Total Registered: $($files.Count)"
$report += ""

if ($frozen.Count -gt 0) {
    $report += "FROZEN ($($frozen.Count) files):"
    foreach ($f in $frozen | Sort-Object) {
        $report += "  - $f"
        if ($files[$f].reason) {
            $report += "    Reason: $($files[$f].reason)"
        }
    }
    $report += ""
}

if ($stable.Count -gt 0) {
    $report += "STABLE ($($stable.Count) files):"
    foreach ($f in $stable | Sort-Object) {
        $report += "  - $f"
        if ($files[$f].reason) {
            $report += "    Reason: $($files[$f].reason)"
        }
    }
    $report += ""
}

if ($repair.Count -gt 0) {
    $report += "REPAIR ($($repair.Count) files):"
    foreach ($f in $repair | Sort-Object) {
        $report += "  - $f"
        if ($files[$f].reason) {
            $report += "    Reason: $($files[$f].reason)"
        }
    }
    $report += ""
}

if ($observe.Count -gt 0) {
    $report += "OBSERVE ($($observe.Count) files):"
    foreach ($f in $observe | Sort-Object) {
        $report += "  - $f"
    }
    $report += ""
}

# Find unregistered Python scripts
$allPyFiles = @()
$scanDirs = @("scripts", "tools", "core", "utils")
foreach ($dir in $scanDirs) {
    $dirPath = Join-Path $repoRoot $dir
    if (Test-Path $dirPath) {
        $pyFiles = Get-ChildItem -Path $dirPath -Filter "*.py" -Recurse -File
        foreach ($pyFile in $pyFiles) {
            $relativePath = $pyFile.FullName.Replace("$repoRoot\", "").Replace("\", "/")
            $allPyFiles += $relativePath
        }
    }
}

$unregistered = $allPyFiles | Where-Object { -not $files.ContainsKey($_) }

if ($unregistered.Count -gt 0) {
    $report += "UNREGISTERED ($($unregistered.Count) files - default to OBSERVE):"
    foreach ($f in $unregistered | Sort-Object) {
        $report += "  - $f"
    }
    $report += ""
}

$report += "=" * 60
$report += "VERDICT: $($frozen.Count) FROZEN, $($stable.Count) STABLE, $($repair.Count) REPAIR, $($observe.Count) OBSERVE, $($unregistered.Count) UNREGISTERED"

# Write report
$report | Out-File -FilePath $outputFile -Encoding UTF8

# Output to console
$report | ForEach-Object { Write-Host $_ }

Write-Host "`n[OK] Report saved to: $outputFile" -ForegroundColor Green
exit 0
