# Court Sweep Report
- ts_utc: 20251230T010709Z
- verdict: **NO-GO**
- reason: Failures: state_history_witness, evidence_index, encoding_reports_present, receipt_validation, state_history_format | Warnings: bundle_uniformity, script_state_lookout

## [PASS] db_counts
- status: **PASS**
- details: `{"status": "PASS", "db": "C:\\Users\\Owner\\Desktop\\PROJECTS IN MOTION\\MarcusGarvey App WWMD\\src\\solob wrapper ARK v0\\solob-wrapper after abc real4plus\\data\\memory.db", "anchors": 8, "chunks": 704}`

## [FAIL] state_history_witness
- status: **FAIL**
- reason: `missing docs/STATE_HISTORY.md`
- details: `{"status": "FAIL", "reason": "missing docs/STATE_HISTORY.md"}`

## [FAIL] evidence_index
- status: **FAIL**
- reason: `missing evidence/INDEX.json`
- details: `{"status": "FAIL", "reason": "missing evidence/INDEX.json"}`

## [WARN] bundle_uniformity
- status: **WARN**
- reason: `no bundles found`
- details: `{"status": "WARN", "reason": "no bundles found"}`

## [FAIL] encoding_reports_present
- status: **FAIL**
- reason: `missing evidence/audits`
- details: `{"status": "FAIL", "reason": "missing evidence/audits"}`

## [FAIL] receipt_validation
- status: **FAIL**
- details: `{"status": "FAIL", "total_receipts": 9, "validated": 0, "invalid": [{"cmd": ["C:\\Users\\Owner\\AppData\\Local\\Programs\\Python\\Python313\\python.exe", "-X", "utf8", "C:\\Users\\Owner\\Desktop\\PROJECTS IN MOTION\\MarcusGarvey App WWMD\\src\\solob wrapper ARK v0\\solob-wrapper after abc real4plus\\scripts\\validate_receipt_v2.py", "C:\\Users\\Owner\\Desktop\\PROJECTS IN MOTION\\MarcusGarvey App `

## [PASS] orphan_chunks
- status: **PASS**
- details: `{"status": "PASS", "orphan_chunks_null_sid": 0, "samples": []}`

## [PASS] bundle_layout
- status: **PASS**
- details: `{"status": "PASS", "total_bundles": 0, "v2_compliant": 0, "v1_legacy": 0, "court_sweep_skipped": 1, "non_compliant": []}`

## [FAIL] state_history_format
- status: **FAIL**
- details: `{"status": "FAIL", "violations": 0, "warnings": 0, "exit_code": 2}`

## [WARN] script_state_lookout
- status: **WARN**
- reason: `7 warning(s) - Script drift or unauthorized scripts detected`
- details: `{"status": "WARN", "frozen_verified": 1, "stable_verified": 27, "unauthorized": 4, "critical_alerts": 0, "warn_alerts": 7, "reason": "7 warning(s) - Script drift or unauthorized scripts detected"}`
