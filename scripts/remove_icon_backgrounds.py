#!/usr/bin/env python3
"""
Remove solid-color backgrounds from favicon/logo PNGs so they look clean on any theme.
Makes white and near-white pixels transparent. Run from repo root:

  pip install Pillow
  python scripts/remove_icon_backgrounds.py

Writes transparent versions to frontend/public/ as <name>_nobg.png. If the original
file is not locked, also replaces the original and keeps a .bak. Otherwise copy
_nobg.png over the original yourself (e.g. after closing the dev server).
"""
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Install Pillow first: pip install Pillow")
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC = REPO_ROOT / "frontend" / "public"

# PNGs to process (solid background -> transparent). Add/remove as needed.
ICONS = [
    "whirlwindkb_favicon_192.png",
    "whirlwindkb_favicon_512.png",
    "Whirlwind logo12.png",
]

# Pixels with RGB all >= this will be made transparent (handles white/off-white).
WHITE_THRESHOLD = 248


def make_background_transparent(img: Image.Image, threshold: int = WHITE_THRESHOLD) -> Image.Image:
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        r, g, b, a = item
        if r >= threshold and g >= threshold and b >= threshold:
            new_data.append((r, g, b, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img


def main():
    for name in ICONS:
        path = PUBLIC / name
        if not path.exists():
            print(f"Skip (not found): {path}")
            continue
        try:
            img = Image.open(path).copy()
            img.load()
            out = make_background_transparent(img)
            # Always write to _nobg file (no lock on new file)
            stem = path.stem
            suffix = path.suffix
            out_path = path.parent / f"{stem}_nobg{suffix}"
            out.save(out_path, "PNG")
            print(f"OK: {name} -> {out_path.name}")
            # Optionally replace original if not locked
            try:
                backup = path.with_suffix(path.suffix + ".bak")
                if path.exists():
                    path.rename(backup)
                out_path.rename(path)
                print(f"     Replaced original (backup: {backup.name})")
            except OSError:
                print(f"     Original locked; use {out_path.name} and replace when dev server/IDE closed.")
        except Exception as e:
            print(f"Error {name}: {e}")


if __name__ == "__main__":
    main()
