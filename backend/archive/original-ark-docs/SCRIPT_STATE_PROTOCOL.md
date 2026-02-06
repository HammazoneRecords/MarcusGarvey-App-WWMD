# SCRIPT_STATE_PROTOCOL.md

**Purpose**: Define script state governance system to prevent AI from silently editing stable/settled scripts.

**Last Updated**: 2025-12-28T01:45:35-05:00

---

## Overview

The Script State Governance system implements "nuh change wah good already" by requiring explicit user consent before AI can modify STABLE or FROZEN scripts.

**Core Principle**: AI must scan the registry, classify files by state, and request permission before editing settled code.

---

## Script States

### DRAFT
- **Definition**: Free to change without restriction
- **Use Case**: New features, experimental code, prototypes
- **AI Behavior**: May edit freely
- **Transition To**: OBSERVE (when ready for review)

### OBSERVE
- **Definition**: Read + analyze; propose changes only
- **Use Case**: Code under review, uncertain quality
- **AI Behavior**: May analyze and propose, but not edit
- **Transition To**: REPAIR (when issues identified), STABLE (when verified)

### REPAIR
- **Definition**: Changes allowed in scoped areas only
- **Use Case**: Scripts with known issues, active development
- **AI Behavior**: May edit within allowed_changes scope
- **Transition To**: STABLE (after verification), OBSERVE (if issues found)

### STABLE
- **Definition**: No edits without explicit user consent (SETTLED)
- **Use Case**: Verified, production-ready code
- **AI Behavior**: **MUST REQUEST USER CONSENT** before any edit
- **Transition To**: REPAIR (if bugs found), FROZEN (if critical)

### FROZEN
- **Definition**: Never edit; replacement only (new file)
- **Use Case**: Cryptographic code, schemas, constitutions
- **AI Behavior**: **NEVER EDIT** - propose new file instead
- **Stamping**: **REQUIRED** (SHA256 verification)
- **Transition To**: None (permanent)

### HOLSTERED
- **Definition**: Tracked but not stamped; actively changing or pending work
- **Use Case**: Files in active development, pending formatting, or frequently updated
- **AI Behavior**: May edit with caution; changes expected
- **Stamping**: **NOT REQUIRED** (file is expected to change)
- **Transition To**: STABLE (when ready to lock), REPAIR (if issues found)

---

## AI Behavior Protocol

When asked to implement a feature, AI must follow this sequence:

### 1. SCAN
- Read `docs/SCRIPT_STATE_REGISTRY.json`
- Identify all files that would be affected by the change

### 2. CLASSIFY
- Determine the state of each affected file
- Files not in registry default to OBSERVE

### 3. PLAN
- Group files by state
- Identify which changes require user consent

### 4. ASK
- If any STABLE/FROZEN files would be edited -> **REQUEST USER CONSENT**
- Present change set grouped by permission level

### 5. EXECUTE
- Only edit allowed files
- For STABLE files: wait for explicit user approval
- For FROZEN files: propose new file instead

---

## Change Set Output Format

When proposing changes, AI must output:

```
CHANGE SET

Must change:
- tools/encoding_report.ps1 (STATE: REPAIR) ? add flag -deep
- docs/STATE_HISTORY.md (STATE: DRAFT) ? format rules section

Should not change (SETTLED):
- docs/ENCODING_CONSTITUTION.md (STATE: STABLE) ? no edits allowed

Optional new files:
- tools/encoding_report_lint.ps1 ? new linter tool instead of modifying settled file

Requires consent:
- core/parser.py (STATE: STABLE) ? change affects chunk boundary logic; request approval
```

---

## Transition Rules

### DRAFT -> OBSERVE
- **Trigger**: Code ready for review
- **Verification**: None required
- **Approval**: Automatic

### OBSERVE -> REPAIR
- **Trigger**: Issues identified, scope defined
- **Verification**: Issue documented in IMPLEMENTATION_DELTA.md
- **Approval**: User confirms scope

### REPAIR -> STABLE
- **Trigger**: All issues resolved, tests passing
- **Verification**: Court sweep PASS, encoding audit clean
- **Approval**: User confirms stability

### STABLE -> FROZEN
- **Trigger**: Code is critical infrastructure
- **Verification**: Cryptographic verification, schema finalization
- **Approval**: User confirms freeze

### STABLE -> REPAIR
- **Trigger**: Bug found, needs fix
- **Verification**: Bug documented with evidence
- **Approval**: User confirms downgrade

---

## Registry Management

### Adding New Files
```yaml
files:
  path/to/new_file.py:
    state: OBSERVE  # Default for new files
    reason: "Brief explanation"
```

### Updating State
```yaml
files:
  path/to/file.py:
    state: STABLE  # Changed from REPAIR
    settled: true
    last_verified: 2025-12-28
    reason: "Court sweep PASS, all tests passing"
```

### Defining Change Policies
```yaml
files:
  path/to/file.py:
    state: STABLE
    allowed_changes:
      - documentation_comments
      - logging_additions
    forbidden_changes:
      - logic_changes
      - import_changes
```

---

## Court Sweep Integration

Court Sweep can verify script states and recommend transitions:

**Checks**:
1. FROZEN files not modified (hash verification)
2. STABLE files have recent verification date
3. REPAIR files have documented issues
4. All critical files are registered

**Recommendations**:
- REPAIR -> STABLE (if tests pass, encoding clean)
- OBSERVE -> REPAIR (if issues found)
- Unregistered files -> OBSERVE (default)

---

## Examples

### Example 1: Editing STABLE File (Requires Consent)

**User Request**: "Add logging to state_transition.py"

**AI Response**:
```
CHANGE SET

Requires consent (STABLE):
- scripts/state_transition.py (STATE: STABLE)
  - Reason: State machine controller
  - Proposed change: Add logging statements
  - Allowed: logging_additions [OK]
  - Forbidden: logic_changes, import_changes

REQUEST: Confirm consent to add logging to STABLE file?
```

### Example 2: Editing FROZEN File (Propose New File)

**User Request**: "Update schema.sql to add new column"

**AI Response**:
```
CHANGE SET

Cannot change (FROZEN):
- data/schema.sql (STATE: FROZEN)
  - Reason: Database schema v1.1 - replacement only
  - Proposed change: Add column

Alternative approach:
- Create: data/schema_v1_2.sql (NEW FILE)
- Create: scripts/migrate_v1_1_to_v1_2.py (MIGRATION)
- Update: docs/SCHEMA_MIGRATION_GUIDE.md (DOCUMENTATION)

REQUEST: Confirm approach to create new schema version?
```

### Example 3: Editing REPAIR File (Allowed)

**User Request**: "Fix bug in mw.py"

**AI Response**:
```
CHANGE SET

May change (REPAIR):
- tools/cli/mw.py (STATE: REPAIR)
  - Reason: MW CLI tool - actively being extended
  - Proposed change: Fix roadblock counting bug
  - Allowed: error_handling [OK]

Proceeding with fix...
```

---

## Philosophy

*"The registry is the contract. The AI is the executor. The user is the authority."*

**Settled files are sacred**: AI must respect the STABLE/FROZEN states and request consent.

**Transparency over convenience**: Better to ask than to silently break working code.

**Forward only**: If a FROZEN file needs changes, create a new version rather than modifying the original.

---

**END OF SCRIPT STATE PROTOCOL**
