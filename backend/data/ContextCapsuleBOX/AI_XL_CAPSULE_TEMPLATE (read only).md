# AI CONTEXT CAPSULE FORMAT v1.2 ? IDE RUNTIME

## Purpose

Provide a stable, minimal, execution-safe context for an AI operating inside an IDE, so it can reason, generate, and modify code without drifting, hallucinating architecture, or breaking invariants.

**This file is intended to be:**
- Copied to clipboard
- Renamed to `AI_XL_CAPSULE_YYYY-MM-DD_HHMM.md` using **Kingston local time (UTC-5)** in 24-hour format
  - Example: `AI_XL_CAPSULE_2025-12-28_1400.md` (2:00 PM Kingston time)
  - **NOT UTC** - Use actual local Jamaica time when file is created
- Added to: `ContextCapsuleBOX/XL_CAPSULE_BOX/` (relative to repository root)
- Loaded at session start
- Referenced before any non-trivial code change
- Updated only when architecture or intent changes

**Version History:**
- v1.3 (2025-12-28): Added section 20 (Honorable Mentions - 16 bar freestyle zone)
- v1.2 (2025-12-28): Added sections 11-19, loud error handling, Solob-specific governance
- v1.1: Added sections 8-10
- v1.0: Initial template

---

## 1. SYSTEM IDENTITY

**Project Name:**  
`[ ]`

**Repository Root:**  
`[ absolute or relative path ]`

**Primary Objective** (1?2 lines, OUTPUT only):  
What this system is supposed to produce or do when complete.

**Non-Goals** (hard constraints):
- [ explicitly not building X ]
- [ explicitly not supporting Y ]

---

## 2. EXECUTION MODE

**AI Role** (select one or define):
- ? Code generator
- ? Refactor assistant
- ? Bug-fix / diagnostics
- ? Test writer
- ? Architecture assistant
- ? Other: [ ]

**Permission Level:**
- ? Read-only (analyze, explain)
- ? Write code (local changes)
- ? Propose changes only (no direct edits)

**Exploration Policy:**
- ? May explore / suggest alternatives
- ? Must execute only (no ideation)

---

## 3. ARCHITECTURAL FREEZE

This section defines what the AI must treat as ground truth.

### Languages / Runtimes

**Language(s):** `[ ]`  
**Runtime(s):** `[ ]`  
**Version constraints:** `[ ]`

### Core Architecture (brief)

**Entry points:**  
`[ ]`

**Core modules:**  
`[ ]`

**Data flow summary:**  
`[ ]`

### Change Permissions

**Files / Directories that MUST NOT be changed:**
- `[ ]`
- `[ ]`

**Files / Directories that MAY be changed:**
- `[ ]`
- `[ ]`

---

## 4. LOCKED DEFINITIONS (DO NOT REINTERPRET)

These terms have caused drift or ambiguity before.

| Term | Operational Definition |
|------|------------------------|
| `[ ]` | `[ ]` |
| `[ ]` | `[ ]` |
| `[ ]` | `[ ]` |

**Explicitly NOT equivalent:**  
`[ ]` ? `[ ]`

---

## 5. ACTIVE ASSUMPTIONS

These guide current implementation. They may be revised, but not silently.

- **A1:** `[ ]`
- **A2:** `[ ]`
- **A3:** `[ ]`

**Assumptions under review** (do not build on):  
`[ ]`

---

## 6. CONSTRAINTS & INVARIANTS

### Functional Constraints
- **Must do:** `[ must do X ]`
- **Must NOT do:** `[ must not do Y ]`

### Non-Functional Constraints

**Performance:**  
`[ ]`

**Security:**  
`[ ]`

**Portability:**  
`[ ]`

**Determinism:**  
`[ ]`

### Coding Standards

**Style guide:**  
`[ ]`

**Linting rules:**  
`[ ]`

**Formatting rules:**  
`[ ]`

---

## 7. CURRENT TASK CONTEXT

**Active Task ID / Name:**  
`[ ]`

**What the AI should do NOW** (one instruction):  
`[ ]`

**What the AI should NOT do in this task:**
- `[ ]`
- `[ ]`

---

## 8. VERIFICATION & SAFETY CHECK

Before responding or writing code, the AI must check:

- ? Does this change violate Non-Goals?
- ? Does it break a Locked Definition?
- ? Does it modify frozen files?
- ? Does it assume missing context?
- ? Does it introduce a new dependency?

**If any are true -> STOP and ask.**

---

## 9. OUTPUT EXPECTATIONS

**Preferred output format:**
- ? Code diff
- ? Full file
- ? Patch only
- ? Explanation first, code second
- ? Code only, no explanation

**Testing expectation:**
- ? Include tests
- ? Do not touch tests
- ? Propose tests only

---

## 10. CONTINUITY NOTE (OPTIONAL)

**What must not be forgotten across IDE sessions:**
- `[ ]`
- `[ ]`

---

## 11. DEPENDENCY MANAGEMENT

**When new dependencies may be added:**
- ? Never (frozen dependency tree)
- ? With explicit approval only
- ? If meets criteria: [ security, licensing, size constraints ]

**Dependency vetting checklist:**
- [ ] License compatible?
- [ ] Actively maintained?
- [ ] Security audit passed?
- [ ] Size/performance acceptable?

---

## 12. ERROR HANDLING POLICY (LOUD & CONTEXTUAL)

**AI Implementation Rules:**
- **FAILED FAST & LOUD**: No silent failures allowed. If an error occurs, the system must halt or report immediately.
- **CONTEXTUAL LOGGING**: Every error must be logged with specific context.
- **ACTION INTENT**: Error reports **MUST** include exactly two sentences describing what the system was trying to accomplish at the moment of failure.

**AI must:**
- ? Fail fast (no silent failures)
- ? Propose recovery options
- ? Log errors with context and intent
- ? Never swallow exceptions without justification

---

## 13. DOCUMENTATION REQUIREMENTS

**Every code change must include:**
- ? Inline comments for non-obvious logic
- ? Docstrings for public APIs
- ? README updates if user-facing
- ? CHANGELOG entry if significant

**Documentation format:**
- Style: [ JSDoc / Sphinx / custom ]
- Minimum: [ one-liner / detailed / examples required ]

---

## 14. EXTERNAL REFERENCES

**Where to find:**
- Design docs: [ path or URL ]
- API specs: [ path or URL ]
- Architecture diagrams: [ path or URL ]
- Decision records: [ path or URL ]

**Canon source of truth for conflicts:**
1. [ Execution Output Logs + Receipts ]
2. [ docs/ SPEC FILES ]
3. [ ANTIFRAGILITY_CONTEXT_ACDOC.md ]
4. [ This Capsule ]

---

## 15. KNOWN ISSUES / TECHNICAL DEBT

**Do NOT fix without approval:**
- [ known issue 1 - under observation ]
- [ known issue 2 - requires design change ]

**Safe to address:**
- [ minor issue 1 ]
- [ minor issue 2 ]

**Workarounds currently in place:**
- [ workaround 1: why it exists, what it prevents ]

---

## 16. VERIFICATION REQUIREMENTS (SOLOB-SPECIFIC)

**Before claiming "done", AI must propose:**
- What artifact proves it worked (receipt, log, output file)
- What the success criteria are (exit code 0, specific text in output)
- How human can verify independently

**Reference:** `docs/VERIFICATION_ARTIFACT_PRINCIPLE.md`

---

## 17. STATE/MODE AWARENESS (SOLOB-SPECIFIC)

**Current system state:** [ OBSERVE / RECORD / EXECUTE ]

**AI permissions by state:**
- **OBSERVE**: Read-only, document-only, no mutations.
- **RECORD**: May propose changes with receipts; no execution.
- **EXECUTE**: May execute with explicit human confirmation per action.

**Reference:** `docs/ANTIFRAGILITY_CONTEXT_ACDOC.md`

---

## 18. COMMUNICATION PROTOCOL

**Response verbosity:**
- ? Concise (code + one-liner)
- ? Standard (code + brief explanation)
- ? Detailed (code + rationale + alternatives)

**When to ask vs proceed:**
- **ASK if:** violates constraint, missing context, or is a breaking change.
- **PROCEED if:** routine refactor, style fix, or obvious bug fix.

---

## 19. ROLLBACK / SAFETY NET

**If a change breaks something:**
1. Stop and report the failure immediately.
2. Propose a rollback plan.
3. Propose a fix-forward strategy.

**Backup expectation:**
- ? AI assumes Git-based version control for rollbacks.
- ? Manual backup required before any mutation.
- ? Evidence receipts/snapshots required before state changes.

---

## 20. HONORABLE MENTIONS (FREESTYLE ZONE)

**Purpose**: Session-specific narrative, wins, insights, or context that doesn't fit the structured sections above.

**Format**: Maximum 16 bars (lines). Keep it concise, memorable, and relevant to future sessions.

**Examples**:
- Key breakthroughs or "aha moments"
- Unique challenges overcome
- Team shout-outs or collaboration highlights
- Architectural decisions worth remembering
- Performance milestones or speed improvements
- Clever workarounds or elegant solutions
- Lessons that shaped this session's approach
- Cultural or project-specific context

**Your 16 Bars**:
```
[ Line 1 ]
[ Line 2 ]
[ Line 3 ]
[ Line 4 ]
[ Line 5 ]
[ Line 6 ]
[ Line 7 ]
[ Line 8 ]
[ Line 9 ]
[ Line 10 ]
[ Line 11 ]
[ Line 12 ]
[ Line 13 ]
[ Line 14 ]
[ Line 15 ]
[ Line 16 ]
```

---


## OPERATIONAL LAW (IDE EDITION)

**DO NOT GUESS ARCHITECTURE**  
**DO NOT FILL GAPS SILENTLY**  
**DO NOT EXPAND SCOPE**

**IF CONTEXT IS MISSING -> ASK**

---

## UPDATE RULE

**This file changes only when:**
- Architecture changes
- Objective changes
- Constraints change

**Otherwise -> READ ONLY (ASK before modifying)**

**This file does NOT change for:**
- Bug fixes
- Small refactors
- Single-task edits

---

**END OF AI CONTEXT CAPSULE ? IDE RUNTIME**
