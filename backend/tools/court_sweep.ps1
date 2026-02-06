<#
tools/court_sweep.ps1 — One command "Prosecutor Sweep" [ASCII-safe]

Runs:
1) State guard check (docs/STATE.json)
2) DB lexicon counts audit (scripts/audit_lexicon_counts.py)
3) Evidence index headline stats (evidence/INDEX.json)
4) Anchors map status line extracts (docs/ANCHORS_MAP.md)
5) Optional: tools/prove.ps1

Usage:
  .\tools\court_sweep.ps1
  .\tools\court_sweep.ps1 -RepoRoot . -RunProve -RequireAZ
#>

[CmdletBinding()]
param(
    [string]$RepoRoot = ".",
    [switch]$RunProve,
    [switch]$RequireAZ,
    [switch]$LatestSidOnly,
    [switch]$TestScriptParse
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($TestScriptParse) {
    Write-Host "OK: parse"
    exit 0
}

function Section([string]$t) {
    Write-Host "`n--- [ $t ] ---" -ForegroundColor Cyan
}

Push-Location $RepoRoot

try {
    Section "1. STATE GUARD CHECK"
    $statePath = Join-Path $RepoRoot "docs\STATE.json"
    if (Test-Path $statePath) {
        Set-StrictMode -Off
        $state = Get-Content $statePath -Raw | ConvertFrom-Json
        [pscustomobject]@{
            branch      = $state.branch
            state       = $state.state
            recorded_at = $state.recorded_at
            active_sid  = if ($state.active_session_id) { $state.active_session_id } else { "(none)" }
        } | Format-Table -AutoSize
        Set-StrictMode -Version Latest
    }

    Section "2. DATABASE SYNC AUDIT (Layer A)"
    python ".\scripts\audit_lexicon_counts.py" | Select-String -Pattern "TOTAL|Letter"

    Section "3. EVIDENCE MASTER INDEX (Layer C)"
    $indexPath = Join-Path $RepoRoot "evidence\INDEX.json"
    if (Test-Path $indexPath) {
        Set-StrictMode -Off
        $index = Get-Content $indexPath -Raw | ConvertFrom-Json

        $fileCount = 0
        if ($null -ne $index.file_count) {
            $fileCount = [int]$index.file_count
        } elseif ($null -ne $index.files) {
            $fileCount = @($index.files).Count
        }

        $bundleCount = 0
        if ($null -ne $index.bundles) {
            if ($index.bundles -is [System.Collections.IDictionary]) {
                $bundleCount = $index.bundles.Count
            } else {
                $bundleCount = $index.bundles.PSObject.Properties.Count
            }
        }

        $genUtc = if ($index.generated_utc) { $index.generated_utc } else { "UNKNOWN" }

        Write-Output ("Evidence_Files: {0}" -f $fileCount)
        Write-Output ("Bundles_Found : {0}" -f $bundleCount)
        Write-Output ("Generated_UTC : {0}" -f $genUtc)
        Set-StrictMode -Version Latest
    }

    Section "4. VISUAL MAP STATUS"
    $mapPath = Join-Path $RepoRoot "docs\ANCHORS_MAP.md"
    if (Test-Path $mapPath) {
        Get-Content $mapPath | Select-String -Pattern "DB anchors|Manifest files|Registry entries|OK:"
    }

    if ($RunProve) {
        Section "5. POWERSHELL PROVE"
        $proveArgs = @("-EvidenceDir", (Join-Path $RepoRoot "evidence"))
        if ($RequireAZ) { $proveArgs += "-RequireAZ" }
        if ($LatestSidOnly) { $proveArgs += "-LatestSidOnly" }
        
        & (Join-Path $RepoRoot "tools\prove.ps1") @proveArgs
    }

    Write-Host "`nOK: COURT SWEEP COMPLETE" -ForegroundColor Green
}
finally {
    Pop-Location
}
