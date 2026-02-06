# Operator Onboarding Guide ? Solobic Wrapper Ark

**7-Day Path to Independent Operation**

---

## Overview

This guide provides a structured 7-day onboarding plan for new operators. By the end of week 1, you'll be capable of independently maintaining and operating Solobic Wrapper Ark.

**Prerequisites**:
- Python 3.9+ familiarity
- SQL basics
- Command-line comfort
- VSCode (recommended)

---

## Day 1: Installation & System Tour

### Morning (2 hours)

**Reading** (90 minutes):
- [ ] [RELEASE_NOTES_V0.md](v0-release/RELEASE_NOTES_V0.md) ? Overview
- [ ] [INSTALLATION.md](v0-release/INSTALLATION.md) ? Setup guide
- [ ] [QUICK_START.md](v0-release/QUICK_START.md) ? 5-minute quickstart

**Installation** (30 minutes):
- [ ] Verify Python version (`python --version`)
- [ ] Navigate to repository directory
- [ ] Run court sweep: `python tools/court_sweep.py`
- [ ] Expected: `[VERDICT] PASS`

### Afternoon (2 hours)

**System Tour** (with mentor):
- [ ] Directory structure walkthrough
- [ ] Database inspection (`Browse data/memory.db` in DB Browser)
- [ ] Evidence bundles review (`ls evidence/bundles/`)
- [ ] State files (`docs/STATE.json`, `docs/STATE_HISTORY.md`)

**Hands-On** (supervised):
- [ ] Check current state: `python tools/cli/mw.py state`
- [ ] View recent court sweep report
- [ ] Query database for anchor count
- [ ] List ritual configs: `ls config/rituals/`

**Day 1 Homework**:
- [ ] Read [V0_ARCHITECTURE.md](v0-release/V0_ARCHITECTURE.md) (skim, focus on 6 Realities)
- [ ] Familiarize with command-line tools

---

## Day 2: Documentation Deep Dive

### Morning (3 hours)

**Reading**:
- [ ] [V0_ARCHITECTURE.md](v0-release/V0_ARCHITECTURE.md) ? System architecture (full read)
- [ ] [FEATURES_V0.md](v0-release/FEATURES_V0.md) ? Feature catalog
- [ ] [EVIDENCE_V0.md](v0-release/EVIDENCE_V0.md) ? Completion proof

**Key Concepts to Understand**:
- [ ] 6 Realities framework
- [ ] STGRAIL principles
- [ ] Witness epoch
- [ ] State discipline (OBSERVE/RECORD/EXECUTE/REPAIR)

### Afternoon (2 hours)

**Hands-On Practice**:
- [ ] Run daily health check (see [COMMON_WORKFLOWS.md](COMMON_WORKFLOWS.md) Workflow 1)
- [ ] View receipts: `cat evidence/bundles/*/RECEIPTS/*.json`
- [ ] Query chunks by anchor: `sqlite3 data/memory.db "SELECT COUNT(*), anchor_id FROM chunks GROUP BY anchor_id;"`
- [ ] Check for orphans (expected: 0)

**Day 2 Homework**:
- [ ] Read [OPERATORS_GUIDE.md](v0-release/OPERATORS_GUIDE.md)
- [ ] Review [COMMON_WORKFLOWS.md](COMMON_WORKFLOWS.md) workflows 1-5

---

## Day 3: Daily Operations (Supervised)

### Morning (2 hours)

**Daily Health Check** (mentor observes):
- [ ] Check system state
- [ ] Run court sweep
- [ ] Review report for any warnings
- [ ] Check orphan count
- [ ] Document findings

**State Management Practice**:
- [ ] Review state history: `cat docs/STATE_HISTORY.md`
- [ ] Practice dry-run state transition (don't execute):
  ```bash
  # Review command structure only
  python scripts/log_state_transition.py --help
  ```

### Afternoon (2 hours)

**Evidence Review**:
- [ ] Find latest court sweep bundle
- [ ] Read REPORT.md
- [ ] Inspect INDEX.json structure
- [ ] Review 3 different receipts
- [ ] Understand receipt schema

**Database Exploration**:
- [ ] Count total chunks
- [ ] List all anchors
- [ ] Find chunks for specific anchor
- [ ] Verify foreign key relationships

**Day 3 Homework**:
- [ ] Read [TROUBLESHOOTING_PLAYBOOK.md](TROUBLESHOOTING_PLAYBOOK.md)
- [ ] Review common failure scenarios

---

## Day 4: Test Ritual Execution (Dry-Run)

### Morning (2 hours)

**Ritual Engine Overview** (mentor explains):
- [ ] Ritual engine architecture
- [ ] Config file structure
- [ ] Module types (JSON, Lexicon, PDF, Registry)
- [ ] Dry-run vs. live execution

**Config Review**:
- [ ] Open `config/rituals/lexicon_a_template.json`
- [ ] Understand each field
- [ ] Review ritual validation process

### Afternoon (3 hours)

**Dry-Run Execution** (supervised):
- [ ] Validate ritual config:
  ```bash
  python tools/cli/mw.py ritual validate --config config/rituals/lexicon_a_template.json
  ```

- [ ] Run dry-run:
  ```bash
  python scripts/ritual_engine.py --config config/rituals/lexicon_a_template.json --dry-run
  ```

- [ ] Review output (no database changes)
- [ ] Understand expected chunks

**Debrief**:
- [ ] What would happen in live execution?
- [ ] How is receipt generated?
- [ ] What court sweep checks would validate this?

**Day 4 Homework**:
- [ ] Create custom ritual config (practice, don't execute)
- [ ] Review workflows 6-10 in COMMON_WORKFLOWS.md

---

## Day 5: Simulated Failure Handling

### Morning (2 hours)

**Failure Scenarios** (mentor simulates):

**Scenario 1: Orphan Chunks**
- [ ] Mentor creates test orphan
- [ ] You run court sweep (expect FAIL)
- [ ] You diagnose using troubleshooting playbook
- [ ] You propose fix (don't execute)
- [ ] Mentor validates approach

**Scenario 2: Invalid Receipt**
- [ ] Mentor provides corrupted receipt
- [ ] You validate receipt
- [ ] You identify specific schema violation
- [ ] You propose fix

### Afternoon (2 hours)

**Scenario 3: State Transition Issue**
- [ ] Review state history for anomaly (planted by mentor)
- [ ] Identify missing SID
- [ ] Propose correction

**Scenario 4: Database Query Performance**
- [ ] Run slow query (mentor provides)
- [ ] Diagnose issue
- [ ] Propose optimization

**Debrief**:
- [ ] Review troubleshooting approach
- [ ] Discuss escalation paths
- [ ] When to contact senior operator?

**Day 5 Homework**:
- [ ] Review all documentation
- [ ] Prepare questions for Day 6

---

## Day 6: Independent Practice Day

### Morning (3 hours)

**Solo Operations** (mentor available for questions):
- [ ] Perform daily health check independently
- [ ] Review last week's court sweep trend
- [ ] Check evidence bundle storage
- [ ] Perform database backup (practice)

**Create Custom Ritual** (supervised from distance):
- [ ] Design ritual config for hypothetical data source
- [ ] Validate config
- [ ] Explain ingestion logic to mentor
- [ ] Get feedback

### Afternoon (2 hours)

**Knowledge Check**:
- [ ] Explain 6 Realities to mentor
- [ ] Describe V2 receipt schema from memory
- [ ] Walk through court sweep check meanings
- [ ] Demonstrate state transition workflow

**Practice Emergency Procedures**:
- [ ] How to restore from backup
- [ ] How to handle database corruption
- [ ] When to escalate vs. self-resolve

**Day 6 Homework**:
- [ ] Final review of all documentation
- [ ] Prepare for Day 7 certification

---

## Day 7: Certification & Handoff

### Morning (2 hours)

**Competency Demonstration**:

1. **Daily Health Check** (unassisted):
   - [ ] Execute complete workflow
   - [ ] Document findings
   - [ ] Mentor scores: PASS / NEEDS REVIEW

2. **Ritual Execution** (full end-to-end):
   - [ ] Transition to RECORD
   - [ ] Validate test ritual config
   - [ ] Execute test ritual (mentor-provided safe config)
   - [ ] Verify receipt generation
   - [ ] Run court sweep
   - [ ] Return to OBSERVE
   - [ ] Mentor scores: PASS / NEEDS REVIEW

### Afternoon (2 hours)

3. **Troubleshooting Exercise**:
   - [ ] Court sweep FAIL scenario (planted)
   - [ ] Diagnose issue independently
   - [ ] Implement fix
   - [ ] Verify with court sweep
   - [ ] Mentor scores: PASS / NEEDS REVIEW

4. **Knowledge Verification**:
   - [ ] Explain state discipline
   - [ ] Describe witness epoch
   - [ ] Walk through evidence chain of custody
   - [ ] Mentor scores: PASS / NEEDS REVIEW

### Certification

**Passing Criteria** (4/4 PASS required):
- [ ] Daily operations competent
- [ ] Ritual execution successful
- [ ] Troubleshooting effective
- [ ] Knowledge comprehensive

**If NEEDS REVIEW**: Additional 1-2 days training on weak areas

**If PASS**: Certified for independent operation!

---

## Post-Certification

### Week 2 Expectations

**You should now be able to**:
- [OK] Perform daily health checks independently
- [OK] Execute rituals end-to-end
- [OK] Diagnose and fix common issues
- [OK] Maintain evidence integrity
- [OK] Escalate appropriately when needed

**Mentor remains available**:
- As-needed support for complex scenarios
- Weekly check-ins (first month)
- Review of first independent ingestion

### Continuing Education

**Optional advanced topics**:
- Custom module development
- Performance optimization
- Advanced SQL queries
- Receipt forensics techniques
- Evidence pack consolidation

---

## Certification Checklist

**Day 1**:
- [ ] System installed and verified
- [ ] Documentation overview complete
- [ ] Basic commands executed

**Day 2**:
- [ ] Architecture understood
- [ ] Features catalog reviewed
- [ ] Daily health check practiced

**Day 3**:
- [ ] Supervised daily operations successful
- [ ] Evidence review completed
- [ ] Database queries comfortable

**Day 4**:
- [ ] Ritual dry-run executed
- [ ] Config structure understood
- [ ] Custom config created (practice)

**Day 5**:
- [ ] Simulated failures handled
- [ ] Troubleshooting skills demonstrated
- [ ] Escalation paths understood

**Day 6**:
- [ ] Independent operations successful
- [ ] Knowledge check passed
- [ ] Emergency procedures understood

**Day 7**:
- [ ] All competency demonstrations: PASS
- [ ] Certified for independent operation

---

**Welcome to the team!** You're now a certified Solobic Wrapper Ark operator.

---

END OF OPERATOR ONBOARDING GUIDE
