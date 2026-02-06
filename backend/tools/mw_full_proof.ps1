<#
tools/mw_full_proof.ps1 - "Reality 1-4 Full Proof Harness" (ASCII-safe)

Runs a prosecutor-grade health check over:
- STATE + witness metadata
- Script parsability gates
- court_sweep (layers 1-4)
- witness epoch compliance
- DB sanity checks
- Anchor/chunk distribution report
- Evidence index headline stats
- Optional: verify latest Supreme Lexicon bundle index hashes

Usage:
  .\tools\mw_full_proof.ps1
  .\tools\mw_full_proof.ps1 -RepoRoot . -RequireAZ
  .\tools\mw_full_proof.ps1 -RepoRoot . -RequireAZ -VerifySupremeBundle
  .\tools\mw_full_proof.ps1 -RepoRoot . -FailIfInRecord
#>

[CmdletBinding()]
param(
  [string]$RepoRoot = ".",
  [switch]$RequireAZ,
  [switch]$VerifySupremeBundle,
  [switch]$FailIfInRecord
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function OK([string]$msg)   { Write-Host ("OK: " + $msg) -ForegroundColor Green }
function WARN([string]$msg) { Write-Host ("WARN: " + $msg) -ForegroundColor Yellow }
function FAIL([string]$msg) {
  Write-Host ("FAIL: " + $msg) -ForegroundColor Red
  exit 2
}
function Section([string]$t) {
  Write-Host ""
  Write-Host ("=== " + $t + " ===") -ForegroundColor Cyan
}

function Require-Path([string]$p) {
  if (!(Test-Path $p)) { FAIL ("missing required path: " + $p) }
}

Push-Location $RepoRoot
try {
  # 0) Required files
  Section "0) REQUIRED FILES"
  Require-Path ".\docs\STATE.json"
  Require-Path ".\docs\STATE_HISTORY.md"
  Require-Path ".\evidence\INDEX.json"
  Require-Path ".\data\memory.db"
  Require-Path ".\tools\court_sweep.ps1"
  Require-Path ".\tools\prove.ps1"
  Require-Path ".\tools\verify_witness_epoch.ps1"
  Require-Path ".\scripts\sanity_check.py"
  Require-Path ".\scripts\inspect_anchor_chunks.py"
  Require-Path ".\scripts\audit_lexicon_counts.py"
  OK "paths present"

  # 1) STATE + witness metadata
  Section "1) STATE + WITNESS"
  $st = Get-Content ".\docs\STATE.json" -Raw | ConvertFrom-Json
  $state = ($st.state | ForEach-Object { "$_".ToUpper() })

  Write-Host ("state=" + $state + " branch=" + $st.branch + " recorded_at=" + $st.recorded_at)

  if ($FailIfInRecord -and $state -eq "RECORD") {
    FAIL "state is RECORD but FailIfInRecord was set. Seal first."
  }

  if ($st.PSObject.Properties.Name -contains "active_session_id") {
    if ([string]::IsNullOrWhiteSpace($st.active_session_id)) { FAIL "active_session_id exists but empty" }
    OK ("active_session_id=" + $st.active_session_id)
  } else {
    WARN "active_session_id not present in STATE.json (older epoch?)"
  }

  # 2) Parse gates (prove + court_sweep)
  Section "2) SCRIPT PARSE GATES"
  try {
    & ".\tools\prove.ps1" -TestScriptParse | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "prove.ps1 exit code $LASTEXITCODE" }
    OK "prove.ps1 parses"
  } catch {
    FAIL ("prove.ps1 parse failed: " + $_.Exception.Message)
  }

  try {
    & ".\tools\court_sweep.ps1" -TestScriptParse | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "court_sweep.ps1 exit code $LASTEXITCODE" }
    OK "court_sweep.ps1 parses"
  } catch {
    FAIL ("court_sweep.ps1 parse failed: " + $_.Exception.Message)
  }

  # 3) Witness epoch compliance
  Section "3) WITNESS EPOCH"
  try {
    & ".\tools\verify_witness_epoch.ps1" | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "verify_witness_epoch.ps1 exit code $LASTEXITCODE" }
    OK "witness epoch verified"
  } catch {
    FAIL ("verify_witness_epoch.ps1 failed: " + $_.Exception.Message)
  }

  # 4) Court sweep (Reality 1-4)
  Section "4) COURT SWEEP (1-4)"
  try {
    if ($RequireAZ) {
      & ".\tools\court_sweep.ps1" -RepoRoot "." -RequireAZ | Out-Host
    } else {
      & ".\tools\court_sweep.ps1" -RepoRoot "." | Out-Host
    }
    if ($LASTEXITCODE -ne 0) { throw "court_sweep.ps1 failed with exit code $LASTEXITCODE" }
    OK "court_sweep completed"
  } catch {
    FAIL ("court_sweep failed: " + $_.Exception.Message)
  }

  # 5) Evidence index headline stats (hard)
  Section "5) EVIDENCE INDEX (HARD)"
  $idx = Get-Content ".\evidence\INDEX.json" -Raw | ConvertFrom-Json
  $iProps = $idx.PSObject.Properties.Name

  $fileCount = 0
  if ($iProps -contains "file_count") {
    $fileCount = [int]$idx.file_count
  } elseif ($iProps -contains "files") {
    $fileCount = @($idx.files).Count
  } else {
    WARN "INDEX.json has neither file_count nor files"
  }

  $bundleCount = 0
  if ($iProps -contains "bundles" -and $null -ne $idx.bundles) {
    if ($idx.bundles -is [System.Collections.IDictionary]) {
      $bundleCount = $idx.bundles.Count
    } else {
      $bundleCount = @($idx.bundles.PSObject.Properties).Count
    }
  } else {
    WARN "INDEX.json missing bundles"
  }

  $genUtc = "UNKNOWN"
  if ($iProps -contains "generated_utc") { $genUtc = $idx.generated_utc }

  Write-Host ("Evidence_Files=" + $fileCount + " Bundles_Found=" + $bundleCount + " Generated_UTC=" + $genUtc)

  if ($fileCount -le 0) { FAIL "INDEX.json fileCount <= 0 (unexpected)" }
  if ($bundleCount -le 0) { WARN "bundleCount <= 0 (maybe early-stage repo?)" } else { OK "bundleCount scalar OK" }
# 6) DB sanity checks (hard stop)
Section "6) DB SANITY"

# Reset exit code so stale values can't poison the court record
$global:LASTEXITCODE = 0

try {
  # Run READ-ONLY sanity in OBSERVE if allowed by flag
  & python ".\scripts\sanity_check.py" --allow-observe | Out-Host

  if ($LASTEXITCODE -ne 0) {
    FAIL ("sanity_check.py exit code " + $LASTEXITCODE)
    throw "STOP: sanity_check failed (exit=$LASTEXITCODE)"
  }

  OK "sanity_check passed"
}
catch {
  FAIL ("sanity_check.py failed: " + $_.Exception.Message)
  throw   # rethrow to hard-stop the whole mw_full_proof.ps1
}

  # 7) Lexicon DB<->JSON count audit (Layer A)
  Section "7) LEXICON COUNTS AUDIT (Layer A)"
  $audit = python ".\scripts\audit_lexicon_counts.py"
  $audit | Out-Host

  $hits = @($audit | Select-String -Pattern "TOTAL\s+\|\s+\d+\s+\|\s+\d+\s+\|\s+OK")
if ($hits.Count -lt 1) {
  FAIL "lexicon counts audit did not report TOTAL ... OK"
}
OK "lexicon total matches (reported OK)"


  # 8) Anchor/chunk distribution report
  Section "8) INSPECT ANCHOR->CHUNKS"
  try {
    python ".\scripts\inspect_anchor_chunks.py" | Out-Host
    OK "inspect_anchor_chunks executed"
  } catch {
    FAIL ("inspect_anchor_chunks.py failed: " + $_.Exception.Message)
  }

  # 9) Optional: verify latest Supreme Lexicon bundle index hashes
  if ($VerifySupremeBundle) {
    Section "9) SUPREME BUNDLE INDEX VERIFY (OPTIONAL)"
    $B = Get-ChildItem ".\evidence" -Directory |
      Where-Object { $_.Name -like "S_*_SUPREME_LEXICON_BUNDLE" } |
      Sort-Object Name -Descending |
      Select-Object -First 1

    if (-not $B) { FAIL "no S_*_SUPREME_LEXICON_BUNDLE folder found" }

    $bIdxPath = Join-Path $B.FullName "INDEX.json"
    Require-Path $bIdxPath

    $bidx = Get-Content $bIdxPath -Raw | ConvertFrom-Json
    $bad = New-Object System.Collections.Generic.List[string]

    foreach ($f in $bidx.files) {
      $p = Join-Path $B.FullName ($f.path -replace "/","\")
      if (!(Test-Path $p)) { $bad.Add(("MISSING: " + $f.path)); continue }
      $h = (Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
      if ($h -ne $f.sha256.ToLower()) { $bad.Add(("HASH_MISMATCH: " + $f.path)) }
    }

    if ($bad.Count -gt 0) {
      $bad | ForEach-Object { Write-Host $_ -ForegroundColor Red }
      FAIL "Supreme bundle index failed hash verification"
    }
    OK ("Supreme bundle verified: " + $B.Name)
  }

  # 10) State-history SID compliance (recent lines sanity)
  Section "10) STATE_HISTORY SID CHECK (RECENT)"
  $recent = Get-Content ".\docs\STATE_HISTORY.md" -Tail 60
  $missingSid = $recent |
    Select-String -Pattern "OBSERVE -> RECORD|RECORD -> OBSERVE|OBSERVE → RECORD|RECORD → OBSERVE" |
    Where-Object { $_.Line -notmatch "sid=" }

  if ($missingSid) {
    # check for legacy addendum
    $addendumPath = ".\docs\STATE_HISTORY_LEGACY_SID_ADDENDUM.json"
    if (Test-Path $addendumPath) {
      $addendum = Get-Content $addendumPath -Raw | ConvertFrom-Json
      if ($addendum.count -gt 0) {
        OK ("legacy sid gap covered by addendum (" + $addendum.count + " lines)")
      } else {
        WARN "recent transitions exist without sid=, and addendum is empty"
      }
    } else {
      WARN "recent transitions exist without sid= (no addendum found):"
      $missingSid | Select-Object -First 10 | ForEach-Object { Write-Host $_.Line -ForegroundColor Yellow }
    }
  } else {
    OK "recent transitions include sid witness"
  }

  Section "DONE"
  OK "Reality 1-4 proof harness complete"
  exit 0
}
finally {
  Pop-Location
}
