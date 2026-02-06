#!/usr/bin/env python3
"""
Weekly Evidence Bundle Aggregator

Reality 4 (The Prosecutor): Automated weekly aggregation of evidence bundles.

Purpose:
- Aggregate all bundles from the past 7 days
- Reference Court Sweep bundles and ingestion bundles
- Generate comprehensive weekly report
- Facilitate long-term archival

Usage:
    python scripts/emit_weekly_evidence_bundle.py [--days 7]

Exit Codes:
    0 = Success
    1 = Error
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
BUNDLES_DIR = BASE_DIR / "evidence" / "bundles"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_bundle_timestamp(bundle_id: str) -> datetime | None:
    """Extract timestamp from bundle ID (e.g., S_20251228T165300Z_COURT_SWEEP)"""
    try:
        if bundle_id.startswith("S_"):
            # Format: S_20251228T165300Z_*
            ts_str = bundle_id.split("_")[1] + "T" + bundle_id.split("T")[1].split("Z")[0] + "Z"
            # Parse: 20251228T165300Z
            return datetime.strptime(ts_str[:17], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        elif bundle_id.startswith("WEEKLY_"):
            # Skip weekly bundles
            return None
    except Exception:
        return None
    return None


def find_bundles_in_period(days: int) -> Dict[str, List[Path]]:
    """Find all bundles from the last N days"""
    if not BUNDLES_DIR.exists():
        return {"court_sweep": [], "ingestion": [], "other": []}

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    court_sweep = []
    ingestion = []
    other = []

    for bundle_path in BUNDLES_DIR.iterdir():
        if not bundle_path.is_dir():
            continue
        
        bundle_id = bundle_path.name
        
        # Skip weekly bundles
        if bundle_id.startswith("WEEKLY_"):
            continue
        
        ts = parse_bundle_timestamp(bundle_id)
        if ts is None or ts < cutoff:
            continue
        
        # Categorize by bundle type
        if "COURT_SWEEP" in bundle_id:
            court_sweep.append(bundle_path)
        else:
            # Check if it has an INDEX.json to determine type
            index_path = bundle_path / "INDEX.json"
            if index_path.exists():
                try:
                    index = json.loads(index_path.read_text(encoding="utf-8"))
                    bundle_type = index.get("bundle_type", "unknown")
                    if bundle_type == "ingestion":
                        ingestion.append(bundle_path)
                    else:
                        other.append(bundle_path)
                except Exception:
                    other.append(bundle_path)
            else:
                other.append(bundle_path)
    
    return {
        "court_sweep": sorted(court_sweep, key=lambda p: p.name),
        "ingestion": sorted(ingestion, key=lambda p: p.name),
        "other": sorted(other, key=lambda p: p.name)
    }


def summarize_bundle(bundle_path: Path) -> Dict[str, Any]:
    """Extract summary info from a bundle"""
    index_path = bundle_path / "INDEX.json"
    if not index_path.exists():
        return {"bundle_id": bundle_path.name, "error": "missing INDEX.json"}
    
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        return {
            "bundle_id": bundle_path.name,
            "bundle_type": index.get("bundle_type", "unknown"),
            "bundle_version": index.get("bundle_version", "unknown"),
            "generated_utc": index.get("generated_utc"),
            "summary": index.get("summary", {})
        }
    except Exception as e:
        return {"bundle_id": bundle_path.name, "error": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate weekly evidence bundle aggregation")
    ap.add_argument("--days", type=int, default=7, help="Number of days to aggregate (default: 7)")
    args = ap.parse_args()

    print(f"Aggregating bundles from the last {args.days} days...")
    
    bundles = find_bundles_in_period(args.days)
    total_bundles = sum(len(v) for v in bundles.values())
    
    if total_bundles == 0:
        print(f"No bundles found in the last {args.days} days.")
        return 0
    
    print(f"Found {total_bundles} bundles:")
    print(f"  - Court Sweep: {len(bundles['court_sweep'])}")
    print(f"  - Ingestion: {len(bundles['ingestion'])}")
    print(f"  - Other: {len(bundles['other'])}")
    
    # Calculate date range
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=args.days)
    
    bundle_id = f"WEEKLY_{start_date.strftime('%Y%m%d')}_TO_{end_date.strftime('%Y%m%d')}"
    weekly_dir = BUNDLES_DIR / bundle_id
    weekly_dir.mkdir(parents=True, exist_ok=True)
    
    # Summarize all bundles
    court_sweep_summaries = [summarize_bundle(p) for p in bundles["court_sweep"]]
    ingestion_summaries = [summarize_bundle(p) for p in bundles["ingestion"]]
    other_summaries = [summarize_bundle(p) for p in bundles["other"]]
    
    # Generate INDEX.json
    index = {
        "bundle_version": "V2",
        "bundle_type": "weekly_aggregate",
        "bundle_id": bundle_id,
        "generated_utc": utc_now(),
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": args.days
        },
        "summary": {
            "court_sweeps": len(bundles["court_sweep"]),
            "ingestion_bundles": len(bundles["ingestion"]),
            "other_bundles": len(bundles["other"]),
            "total_bundles": total_bundles
        },
        "references": {
            "court_sweep": court_sweep_summaries,
            "ingestion": ingestion_summaries,
            "other": other_summaries
        }
    }
    
    (weekly_dir / "INDEX.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\\n",
        encoding="utf-8"
    )
    
    # Generate REPORT.md
    report_md = f"""# Weekly Evidence Bundle Report

**Bundle ID**: {bundle_id}  
**Generated**: {utc_now()}  
**Period**: {start_date} to {end_date} ({args.days} days)

## Summary

Aggregated {total_bundles} evidence bundles from the past {args.days} days.

## Breakdown

- **Court Sweeps**: {len(bundles['court_sweep'])}
- **Ingestion Bundles**: {len(bundles['ingestion'])}
- **Other Bundles**: {len(bundles['other'])}

## Court Sweep Bundles

{chr(10).join(f"- {s['bundle_id']} ({s.get('generated_utc', 'N/A')})" for s in court_sweep_summaries) or '(none)'}

## Ingestion Bundles

{chr(10).join(f"- {s['bundle_id']} ({s.get('generated_utc', 'N/A')})" for s in ingestion_summaries) or '(none)'}

## Other Bundles

{chr(10).join(f"- {s['bundle_id']}" for s in other_summaries) or '(none)'}

---

Generated by emit_weekly_evidence_bundle.py
"""
    
    (weekly_dir / "REPORT.md").write_text(report_md, encoding="utf-8")
    
    print(f"\n[OK] Weekly bundle created: {weekly_dir.relative_to(BASE_DIR)}")
    print(f"  - INDEX.json")
    print(f"  - REPORT.md")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
