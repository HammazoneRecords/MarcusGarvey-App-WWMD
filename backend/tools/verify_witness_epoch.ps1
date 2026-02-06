<#
tools/verify_witness_epoch.ps1 — Verify SID witness presence after epoch start.

Usage:
  .\tools\verify_witness_epoch.ps1
  .\tools\verify_witness_epoch.ps1 -HistoryPath docs/STATE_HISTORY.md
#>

[CmdletBinding()]
param(
    [string]$HistoryPath = "docs\STATE_HISTORY.md"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $HistoryPath)) {
    Write-Host "FAIL: History file not found: $HistoryPath" -ForegroundColor Red
    exit 1
}

# Read history. Force UTF-8.
$lines = Get-Content $HistoryPath -Encoding UTF8

$epochStarted = $false
$violations = @()
$lineNum = 0

foreach ($line in $lines) {
    $lineNum++
    $trimmed = $line.Trim()
    
    # Check for marker
    if ($trimmed -match "WITNESS_EPOCH_START:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)") {
        $epochStarted = $true
        continue
    }
    
    if (-not $epochStarted) {
        continue
    }
    
    # Skip headings and empty lines
    if ($trimmed.StartsWith("#") -or [string]::IsNullOrWhiteSpace($trimmed)) {
        continue
    }
    
    # Detect transition lines: look for state keywords + arrow
    # Patterns: OBSERVE, RECORD, EXECUTE
    # Arrows: ->, →
    $isTransition = ($trimmed -match "(OBSERVE|RECORD|EXECUTE)") -and ($trimmed -match "(->|→)")
    
    if ($isTransition) {
        # Check for sid=
        if ($trimmed -notmatch "sid=") {
            $isLegacy = $false
            # Check for legacy addendum
            $addendumPath = Join-Path (Split-Path $HistoryPath) "STATE_HISTORY_LEGACY_SID_ADDENDUM.json"
            if (Test-Path $addendumPath) {
                $addendum = Get-Content $addendumPath -Raw | ConvertFrom-Json
                foreach ($item in $addendum.legacy_transitions_without_sid) {
                    if ($item.line_number -eq $lineNum) {
                        $isLegacy = $true
                        break
                    }
                }
            }

            if (-not $isLegacy) {
                $violations += [pscustomobject]@{
                    LineNumber = $lineNum
                    Content    = $trimmed
                }
            }
        }
    }
}

if ($violations.Count -gt 0) {
    Write-Host "FAIL: Witness violations detected after epoch start!" -ForegroundColor Red
    $violations | Format-Table -AutoSize
    exit 2
}

Write-Host "OK: Witness epoch verified" -ForegroundColor Green
exit 0
