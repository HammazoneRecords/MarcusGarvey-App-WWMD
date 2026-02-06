from pathlib import Path
import re, json

def main():
    p = Path("docs/STATE_HISTORY.md")
    if not p.exists():
        print(f"File not found: {p}")
        return

    text = p.read_text(encoding="utf-8", errors="replace").splitlines()

    # Match common transition arrows and dashes
    pat = re.compile(r"(OBSERVE\s*[->\-]\s*RECORD|RECORD\s*[->\-]\s*OBSERVE)")
    legacy = []
    for i, line in enumerate(text, start=1):
        if pat.search(line) and "sid=" not in line:
            legacy.append({"line_number": i, "line": line})

    out = {
        "addendum_version": "V1",
        "source": "docs/STATE_HISTORY.md",
        "legacy_transitions_without_sid": legacy,
        "count": len(legacy),
    }

    Path("docs/STATE_HISTORY_LEGACY_SID_ADDENDUM.json").write_text(
        json.dumps(out, indent=2),
        encoding="utf-8"
    )

    print("OK: wrote docs/STATE_HISTORY_LEGACY_SID_ADDENDUM.json")
    print("legacy_count=", len(legacy))

if __name__ == "__main__":
    main()
