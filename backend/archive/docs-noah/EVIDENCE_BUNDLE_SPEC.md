# Solob Wrapper ? Evidence Bundle Specification (V1)

Canonical structure for any evidence bundle directory `evidence/<BUNDLE_NAME>/`:

| Path | Type | Description |
| :--- | :--- | :--- |
| `INDEX.json` | File | Comprehensive hash index of all files in this bundle. |
| `BUNDLE.json` | File | Manifest/Contract describing the scope and provenance of data. |
| `RECEIPTS/` | Dir | JSON receipts for each atom of data (e.g., lexicon letters, PDF pages). |
| `STAMPS/` | Dir | (Optional) Audit stamps confirming existence at T0. |
| `LOGS/` | Dir | (Optional) Relevant CLI logs (stdout/stderr) from the creation run. |
| `DB/` | Dir | (Optional) Database checkpoint receipts or partial exports. |

## Invariants
1. All files listed in `INDEX.json` must exist and match their SHA-256.
2. The folder name must match a valid SID pattern: `S_yyyyMMddTHHmmssZ_<TAG>`.
3. Multi-layer proofs (Layer A/B/C) are consolidated into this layout for portability.
