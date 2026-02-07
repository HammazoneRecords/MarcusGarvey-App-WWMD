PWA icons (192×192 and 512×512) are wired as whirlwindkb_favicon_192.png and whirlwindkb_favicon_512.png in vite.config.ts. Favicon: whirlwindkb_favicon.ico. Apple touch icon: Whirlwind logo12.png.

To remove solid backgrounds from these PNGs (e.g. white -> transparent), run from repo root:
  python scripts/remove_icon_backgrounds.py
(Requires: pip install Pillow)
