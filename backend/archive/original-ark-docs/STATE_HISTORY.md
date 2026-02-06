# STATE_HISTORY.md (append-only)

Every time you change STATE.json, you also append:

timestamp

from -> to

who

reason (one line)

---

## WITNESS EPOCH

The "Witness Epoch" marks the point where every state transition began to be automatically tagged with a canonical session ID (`sid=...`). Earlier entries may lack this field as the witness system was introduced mid-project.

Witness Epoch: 2025-12-25T07:51:59Z
WITNESS_EPOCH_START: 2025-12-25T07:51:59Z

### SID Witness Policy
1. Transition notes must include the canonical SID that witnessed the window.
2. The SID is generated during transition to `RECORD`.
3. The same SID is logged during the transition back to `OBSERVE` to seal the window.

### Verification Helper
To find transition lines after the epoch start that lack a SID witness:
`.\tools\verify_witness_epoch.ps1`

---

- 2025-12-28T22:45:00-05:00 (UTC 2025-12-29T03:45:00Z)  NOTE  STATE_HISTORY reset. Previous history (110 transitions) archived to archive/docs-noah/NOAH2_STATE_HISTORY.md.

- 2025-12-28T22:45:21-05:00 (UTC 2025-12-29T03:45:21Z)  NOTE  Official State History reset complete. System now under strict V1.0 format compliance.
- 2025-12-28T22:50:31-05:00 (UTC 2025-12-29T03:50:31Z) - OBSERVE -> RECORD - Beginning Evidence Bundle V2 Migration (Step 1 of Plan) (sid=S_20251225T075155Z_STATE_RECORD)
- 2025-12-28T22:52:41-05:00 (UTC 2025-12-29T03:52:41Z) - RECORD -> OBSERVE - Bundle V2 Migration complete. All integrity checks PASS. Returning to default safe state. (sid=S_20251225T075155Z_STATE_RECORD)
- 2025-12-29T00:38:15-05:00 (UTC 2025-12-29T05:38:15Z) - RECORD -> OBSERVE - Bundle Layout V2 Compliance complete. All 6 Realities achieved (100%). XL Capsule documented. Returning to safe state. (sid=S_20251225T075155Z_STATE_RECORD)