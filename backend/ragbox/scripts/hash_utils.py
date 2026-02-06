from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List, Tuple


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def list_files(root: Path) -> List[Path]:
    # Deterministic ordering
    return sorted([p for p in root.rglob("*") if p.is_file()])


def sha256_manifest(root: Path) -> List[Tuple[str, str]]:
    """
    Returns list of (relative_path, sha256) for every file under root, sorted.
    """
    files = list_files(root)
    out: List[Tuple[str, str]] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        out.append((rel, sha256_file(f)))
    return out
