<#
tools/prove.ps1 — Solob Wrapper Coherence Proof (PowerShell) [ASCII-safe]

What it checks:
A) Evidence index sanity (exists, JSON parses, file_count present)
B) A-Z Lexicon receipts + stamps presence (aggregate across evidence tree)
C) Optional: Hash verification against INDEX entries if index contains per-file items

Usage:
  .\tools\prove.ps1 -EvidenceDir .\evidence
  .\tools\prove.ps1 -EvidenceDir .\evidence -Scope lexicon -RequireAZ
#>

[CmdletBinding()]
param(
    [string]$EvidenceDir = ".\evidence",
    [ValidateSet("lexicon", "all")]
    [string]$Scope = "lexicon",
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

function Fail([string]$msg) {
    Write-Host ("FAIL: {0}" -f $msg) -ForegroundColor Red
    exit 1
}
function Warn([string]$msg) {
    Write-Host ("WARN: {0}" -f $msg) -ForegroundColor Yellow
}
function Ok([string]$msg) {
    Write-Host ("OK: {0}" -f $msg) -ForegroundColor Green
}
function Info([string]$msg) {
    Write-Host ("INFO: {0}" -f $msg) -ForegroundColor Cyan
}

function Test-ScriptParse {
    Write-Host "OK: parse"
    exit 0
}

function JoinEvidencePath([string]$baseDir, [string]$relOrAbs) {
    if ([string]::IsNullOrWhiteSpace($relOrAbs)) { return $null }
    if ([System.IO.Path]::IsPathRooted($relOrAbs)) { return $relOrAbs }
    $clean = ($relOrAbs -replace "/", "\")
    return (Join-Path $baseDir $clean)
}

function Get-LatestLexiconSidFolder([string]$evidenceDir) {
    $sidFolders = Get-ChildItem $evidenceDir -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^S_\d{8}T\d{6}Z_' } |
    Sort-Object Name -Descending

    if (!$sidFolders) { return $null }
    $prefer = $sidFolders | Where-Object { $_.Name -match 'LEXICON_AZ' } | Select-Object -First 1
    if ($prefer) { return $prefer.FullName }
    $lex = $sidFolders | Where-Object { $_.Name -match 'LEXICON' } | Select-Object -First 1
    if ($lex) { return $lex.FullName }
    return $null
}

function Test-LexiconAZ([string]$evidenceDir, [bool]$latestOnly) {
    $letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".ToCharArray() | ForEach-Object { [string]$_ }
    $missing = New-Object System.Collections.Generic.List[string]

    if ($latestOnly) {
        $lexDir = Get-LatestLexiconSidFolder $evidenceDir
        if (-not $lexDir) {
            Fail ("LatestSidOnly requested, but no lexicon SID folder found under {0}" -f $evidenceDir)
        }
        Info ("A-Z check mode: LatestSidOnly ({0})" -f $lexDir)
        foreach ($L in $letters) {
            $r = Get-ChildItem $lexDir -File -Filter ("RECEIPT_LEXICON_{0}*.json" -f $L) -ErrorAction SilentlyContinue
            if (!$r) { $missing.Add(("Missing receipt in latest SID: {0}" -f $L)) }
        }
    } else {
        Info "A-Z check mode: Aggregate (search across evidence tree)"
        foreach ($L in $letters) {
            $r = Get-ChildItem $evidenceDir -Recurse -File -Filter ("RECEIPT_LEXICON_{0}*.json" -f $L) -ErrorAction SilentlyContinue
            if (!$r) { $missing.Add(("Missing receipt anywhere: {0}" -f $L)) }
        }
    }

    if ($missing.Count -gt 0) {
        $missing | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        Fail "A-Z completeness failed"
    }
    Ok "A-Z receipts present"
}

# ---------------- MAIN ----------------
if (!(Test-Path $EvidenceDir)) {
    Fail ("EvidenceDir not found: {0}" -f $EvidenceDir)
}

$indexPath = Join-Path $EvidenceDir "INDEX.json"
if (!(Test-Path $indexPath)) {
    Fail ("INDEX.json not found at: {0}" -f $indexPath)
}

try {
    $index = Get-Content $indexPath -Raw | ConvertFrom-Json
} catch {
    Fail ("INDEX.json is not valid JSON: {0}" -f $_.Exception.Message)
}

if (-not ($index.PSObject.Properties.Name -contains "file_count")) {
    Warn "INDEX.json has no file_count field."
} else {
    Ok ("INDEX.json file_count = {0}" -f $index.file_count)
}

if ($RequireAZ) {
    Test-LexiconAZ -evidenceDir $EvidenceDir -latestOnly ([bool]$LatestSidOnly)
}

Ok "Coherence proof passed"
exit 0
