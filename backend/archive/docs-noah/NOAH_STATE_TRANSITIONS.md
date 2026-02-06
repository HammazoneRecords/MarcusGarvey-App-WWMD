STATE TRANSITION GUARDRAILS (STGRAIL)
VERSION: V1
STATUS: CANONICAL
SCOPE: SOLOB WRAPPER

--------------------------------------------------
PURPOSE
--------------------------------------------------

THIS DOCUMENT DEFINES THE ALLOWED STATES OF OPERATION
AND THE ACTIONS PERMITTED IN EACH STATE.

NO SCRIPT, AI, OR HUMAN MAY PERFORM AN ACTION
OUTSIDE THE PERMISSIONS OF THE CURRENT STATE.

STATE TRANSITIONS MUST BE EXPLICIT AND RECORDED.

--------------------------------------------------
STATES
--------------------------------------------------

STATE 0 ? OBSERVE

DESCRIPTION:
Awareness without action.

ALLOWED:
- Read files
- Review documentation
- Discuss architecture
- Define invariants
- Write plans and prompts
- Generate scripts WITHOUT running them

FORBIDDEN:
- Running any script
- Initializing databases
- Registering anchors
- Importing chunks
- Writing to memory.db
- Creating logs or snapshots

DEFAULT STATE:
YES

--------------------------------------------------

STATE 1 ? RECORD

DESCRIPTION:
Preparation with recording, no mutation of truth sources.

ALLOWED:
- Snapshot anchors (read-only)
- Hash schema.sql
- Create ops ledger entries
- Create logs
- Record intent and environment

FORBIDDEN:
- Modifying anchors
- Importing data into DB
- Executing init_db
- Creating chunks
- Running first audited query

REQUIRES:
- ops_ledger.jsonl active
- Explicit human intent

--------------------------------------------------

STATE 2 ? EXECUTE

DESCRIPTION:
Irreversible actions are permitted with full audit trail.

ALLOWED:
- init_db.py
- register_anchor.py
- import_lexicon_chunks.py
- import_pdf_chunks.py
- first_run_example.py

REQUIRES:
- Prior RECORD state completed
- Anchor snapshot exists
- Human intent declared per action
- run_recorded.py wrapper used

FORBIDDEN:
- Silent execution
- Direct script invocation
- Unrecorded DB writes

--------------------------------------------------
STATE TRANSITIONS
--------------------------------------------------

OBSERVE  -> RECORD
REQUIRES:
- Human declaration of readiness
- Confirmation that anchors exist on disk

RECORD -> EXECUTE
REQUIRES:
- Successful anchor snapshot
- ops ledger active
- No schema changes since snapshot

EXECUTE -> OBSERVE
ALLOWED:
- At any time
- No rollback implied
- Observation resumes with new known state

--------------------------------------------------
ENFORCEMENT PRINCIPLE
--------------------------------------------------

IF A STATE IS NOT DECLARED,
ASSUME OBSERVE.

IF A STATE IS UNCLEAR,
DO NOTHING.

IF AN ACTION CANNOT BE RECORDED,
IT MUST NOT OCCUR.

--------------------------------------------------
CLOSING NOTE
--------------------------------------------------

THIS SYSTEM VALUES TRACEABILITY OVER SPEED.

EVERY SHUFFLE MUST HAVE:
- A STATE
- A REASON
- A RECORD

END OF DOCUMENT.
