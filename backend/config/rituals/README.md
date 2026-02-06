# Ritual Config Directory

This directory contains JSON configuration files for the ritual engine.

## Available Configs

| File | Purpose | Anchor |
|------|---------|--------|
| `lexicon_a_template.json` | Lexicon A ingestion | lexicon_a_v1 |
| `bos_pdf_template.json` | Book of Solobility PDF | book_of_solobility_v1 |
| `registry_template.json` | Anchor registration | (multiple) |

## Usage

```bash
# List all configs
mw ritual list

# Validate config
mw ritual validate --config config/rituals/<file>.json

# Execute ritual
mw ritual run --config config/rituals/<file>.json
```

## Creating New Configs

1. Copy an existing template
2. Update `ritual_name`, `intent`, `anchor_id`
3. Update `source.path` to your data file
4. Adjust `steps` as needed
5. Test with `mw ritual validate`

## Config Schema

See `config/schemas/ritual_config.json` for JSON Schema.

See `docs/RITUAL_ENGINE.md` for full documentation.
