# Court Sweep Report
- ts_utc: 20251229T024830Z
- verdict: **NO-GO**
- reason: Failures: state_history_format | Warnings: bundle_layout

## [OK] db_counts
- status: **PASS**
- details: `{"status": "PASS", "db": "C:\\Users\\Owner\\Desktop\\PROJECTS IN MOTION\\ARK V0\\solob wrapper ARK v0\\solob-wrapper after abc real4plus\\data\\memory.db", "anchors": 31, "chunks": 3446}`

## [OK] state_history_witness
- status: **PASS**
- details: `{"status": "PASS", "epoch": "2025-12-25T07:51:59Z", "checked_blocks": 2, "unwitnessed_blocks": 0, "samples": []}`

## [OK] evidence_index
- status: **PASS**
- details: `{"status": "PASS", "path": "C:\\Users\\Owner\\Desktop\\PROJECTS IN MOTION\\ARK V0\\solob wrapper ARK v0\\solob-wrapper after abc real4plus\\evidence\\INDEX.json", "keys": ["bundles", "file_count", "generated_utc", "kind", "root_rel", "strict", "version"]}`

## [OK] bundle_uniformity
- status: **PASS**
- details: `{"status": "PASS", "checked": 28, "missing": {}}`

## [OK] encoding_reports_present
- status: **PASS**
- details: `{"status": "PASS", "encoding_reports": 2, "compile_reports": 1}`

## [OK] receipt_validation
- status: **PASS**
- details: `{"status": "PASS", "total_receipts": 27, "validated": 27, "invalid": [], "errors": [], "debug_dir": "evidence\\audits\\validation_debug\\20251229T024830Z", "validator_sha256": "9f9123882d31a801321120b25f61f4c689a925a9cf7a9e7f279ca9483136f8fd"}`

## [OK] orphan_chunks
- status: **PASS**
- details: `{"status": "PASS", "orphan_chunks_null_sid": 0, "samples": []}`

## [WARN] bundle_layout
- status: **WARN**
- details: `{"status": "WARN", "total_bundles": 28, "v2_compliant": 0, "v1_legacy": 28, "non_compliant": []}`

## [ERROR] state_history_format
- status: **FAIL**
- details: `{"status": "FAIL", "violations": 72, "warnings": 0, "exit_code": 1}`
