# VERIFICATION_ARTIFACT_PRINCIPLE.md

**Purpose**: Guard against "progress theater" by requiring verification artifacts for every proposed action.

**Philosophy**: *"If you cannot name the receipt that proves it worked, you have not truly planned the work."*

**Last Updated**: 2025-12-27T23:23:24-05:00

---

## Core Principle

**When proposing an action, you must also propose the verification artifact that will prove it worked.**

This prevents:
- [ERROR] Vague implementation claims without proof
- [ERROR] "Done" status without measurable evidence
- [ERROR] Passing tests without receipts
- [ERROR] Feature completion without forensic trail

This ensures:
- [OK] Every action has observable proof
- [OK] Every completion has documentary evidence
- [OK] Every claim has a receipt
- [OK] Every test has a witness

---

## Implementation Template

When proposing any action, include:

### 1. Action Description
What will be done (concise, specific)

### 2. Verification Artifact
What evidence will prove it worked (file, receipt, report, output)

### 3. Success Criteria
What the artifact must contain/show to prove success

---

## Examples

### Example 1: Implementing Court Sweep Command

**Action**: Create unified `scripts/court_sweep.py` command

**Verification Artifacts**:
1. **Execution Output**: ASCII-only stdout showing GO verdict
2. **Exit Code**: `echo $?` returns `0` (GO) or `1` (NO-GO)
3. **Receipt**: `evidence/*/R_*_COURT_SWEEP_*.json` witness receipt
4. **Report**: `docs/court_sweep_output_YYYYMMDD.txt` saved output log

**Success Criteria**:
- Output contains: `VERDICT: GO` or `VERDICT: NO-GO`
- Exit code matches verdict (0=GO, 1=NO-GO)
- Receipt timestamp matches execution time
- Report shows all 6 subsystem checks (constitution, imports, database, receipts, encoding, witness epoch)

---

### Example 2: Encoding Corruption Fix

**Action**: Remove ghost question mark pattern from `scripts/state_transition.py`

**Verification Artifacts**:
1. **Encoding Check**: `file scripts/state_transition.py` shows `UTF-8 Unicode text`
2. **Execution Test**: `python scripts/state_transition.py --help` runs without ImportError
3. **Content Sample**: `head -n 5 scripts/state_transition.py` shows clean imports

**Success Criteria**:
- File command returns UTF-8 (not UTF-16)
- Help output displays usage without errors
- Sample shows `import` not `?i?m?p?o?r?t?`

---

### Example 3: BoS PDF Ingestion

**Action**: Ingest Book of Solobility pages into database

**Verification Artifacts**:
1. **Database Query**: `SELECT COUNT(*) FROM chunks WHERE anchor_id='book_of_solobility'` returns expected count
2. **Receipt Chain**: 
   - `R_*_INGESTION_STARTED_book_of_solobility_*.json`
   - `RECEIPT_CHUNKS_book_of_solobility_*.json`
   - `R_*_INGESTION_COMPLETED_book_of_solobility_*.json`
3. **Forensic Report**: `docs/BOS_INGESTION_FINAL_REPORT.md` with chunk count audit
4. **Citation Test**: `python scripts/cite_bos.py --page 1` returns page 1 text with locator

**Success Criteria**:
- Chunk count = PDF page count - empty pages
- All 3 receipts exist with linked timestamps
- Report shows MATCH for JSON vs DB counts
- Citation test returns exact page text with format `pdf:page:0001:chars:XXXXXX-YYYYYY`

---

## Anti-Patterns (What NOT to Do)

### [ERROR] Anti-Pattern 1: Vague Completion
**Bad**: "Fixed encoding issues"
- **Problem**: No verification artifact specified
- **Fix**: "Fixed encoding issues; verify with `tools/encoding_report.ps1` output showing zero UTF-16 files"

### [ERROR] Anti-Pattern 2: Action Without Evidence
**Bad**: "Ran court sweep, system is healthy"
- **Problem**: No saved output, no receipt, no proof
- **Fix**: "Ran court sweep; see `court_sweep_output_20251227.txt` showing GO verdict + witness receipt `R_20251227_COURT_SWEEP_*.json`"

### [ERROR] Anti-Pattern 3: Test Without Witness
**Bad**: "Tests passing"
- **Problem**: Exit code not captured, output not saved
- **Fix**: "Tests passing (6/6); see `test_output_20251227.txt` with exit code 0"

---

## Integration with IMPLEMENTATION_DELTA.md

Every delta checklist item should follow this pattern:

```markdown
- [ ] [ACTION DESCRIPTION]
  - **Verification**: [artifact type and location]
  - **Success**: [what artifact must show]
```

Example:
```markdown
- [ ] Run encoding audit: `tools/encoding_report.ps1` -> clean report
  - **Verification**: `encoding_report.txt` output file
  - **Success**: Zero UTF-16 files, zero NUL byte files, all ASCII/UTF-8
```

---

## Court-Grade Evidence Standard

For critical actions (security fixes, data migrations, schema changes), require **3-layer proof pyramid**:

1. **Layer A**: Direct evidence (database query, file check, execution output)
2. **Layer B**: Receipt witness (timestamped JSON receipt)
3. **Layer C**: Forensic report (human-readable analysis document)

This creates defensible audit trail that can withstand scrutiny.

---

## Usage Protocol

**Before Action**: Define verification artifacts
**During Action**: Capture artifacts as you work
**After Action**: Validate artifacts meet success criteria
**On Completion**: Reference artifacts in status update

**Philosophy**: *"The artifact is not proof you worked. The artifact is proof it worked."*
