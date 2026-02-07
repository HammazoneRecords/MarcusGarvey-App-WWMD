# Content & Source Attribution

This document records how Whirlwind KB sources and content are managed for publication.

## Source URLs (Knowledge Base)

- **Primary sources** in `frontend/src/mock/db.json` (and backend nodes DB when seeded from it) use direct document links where possible. Archive.org and institutional links (e.g. LoC, NYPL, BlackPast) are used for primary documents.
- **Direct links in place:**
  - **src-unia-const**: BlackPast full text (1918 Constitution) — `https://www.blackpast.org/african-american-history/constitution-universal-negro-improvement-association-1918/`
  - **src-pao-1923**, **src-pao-1925**: Archive.org (Philosophy and Opinions; digitized editions often combine Vol 1 & 2)
  - **src-mtp-1937**: Google Books (Message to the People)
  - **src-negro-world**: LoC item (The Negro World)
  - **src-bsl-records**: NYPL Digital Collections (Black Star Line incorporation)
  - **src-declaration-1920**: Wikisource (Declaration of Rights)
  - **src-harlem-1919**: NYPL Archives (Liberty Hall)
- **Search/discovery links** (use when no single direct document URL exists): **src-convention-1920**, **src-nfc-1920** — archive.org search with descriptive query; excerpt notes direct users to institutional archives for full proceedings/charter.
- **Verification**: Before public launch, verify each `url` in `db.json` opens and matches the cited document. Nodes DB is seeded from `db.json`, so one source of truth.

## Facts and daily content

- **Facts** are intended to be historically accurate and backed by receipts (SourceRef). Have a subject-matter reviewer spot-check a sample (e.g. Black Star Line, Convention 1920, Declaration of Rights, UNIA membership claims) before publication.
- **Daily reflection** content (quotes and context) is attributed via `sourceId` to a source in `db.json`; each quote should trace to the stated source. Spot-check a sample of daily items for accuracy and attribution.

## Gallery images and licensing

- Images live in `frontend/public/assets/gallery/`. Gallery data (captions, years) is in `frontend/src/mock/data.ts` (MOCK_GALLERY).
- **Attribution and licensing:** Confirm licensing for each asset before publication. Current filenames and captions suggest:
  - **marcus-garvey-1887-1940-loc-flickr-the-library-of-congress-5fcd97.jpg** — Library of Congress (caption credits LoC).
  - **service-pnp-ds-17200-17264v.jpg** — LoC Prints & Photographs (caption credits LoC).
  - **marcus-1.jpg**, **marcus-garvey-1922-91d215.jpg**, **marcus-garvey-president-general-of-the-african-republic-news-photo-1737995391.avif** — Verify origin and license (e.g. public domain, LoC, or licensed); add attribution in UI or here if required.
- Gallery UI shows an attribution line: "Historical images: Library of Congress and public domain archives." Update that line if additional sources or attribution are required.

## Quote attribution

- All Garvey quotes and historical text in the app (Knowledge Base, Daily, Toolkit templates) are attributed to the stated source. No unattributed or misattributed content. Legal Disclaimer and Data Disclaimer (Profile) clarify that Garvey Lens is source-grounded, not roleplay or impersonation.

## Legal disclaimer

- The in-app **Legal Disclaimer** (Architectural Boundary card) is shown on **Home** and **Profile**. It states that Whirlwind KB is a source-grounded research instrument and that the Garvey Lens is not roleplay or impersonation. Keep this visible and consistent with Terms of Use and Privacy Policy. Wording is final for pre-publication unless legal review requires changes.
