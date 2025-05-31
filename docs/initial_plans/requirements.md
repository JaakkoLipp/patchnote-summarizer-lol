# Requirements & Backlog

Below is a starter backlog organised by priority buckets.

## MVP Stories

| ID     | Title                   | User story (As a … I want … so that …)                                                                        | Acceptance Criteria                                                                                                       |
| ------ | ----------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| MVP‑01 | Detect new patch        | As a backend worker I want to scan Riot’s updates index so that I know when a new patch article is published. | ✅ Given the HTML fixture for patch index, when the worker runs, it returns the latest patch URL.<br>✅ Unit‑test passes. |
| MVP‑02 | Download & archive HTML | As a backend worker I want to save the full raw HTML into S3 so I can reference it later.                     | ✅ File exists in bucket with key `raw/14.10.html`.<br>✅ MD5 checksum logged.                                            |
| MVP‑03 | Clean & segment text    | As a summariser I want champion sections in clean Markdown so the LLM prompt is consistent.                   | ✅ Function `clean_html()` removes nav/ads and splits on headings.<br>✅ Snapshot test diff = 0.                          |
| MVP‑04 | Summarise one section   | As the system I want to turn a champion section into ≤6 bullet summary.                                       | ✅ Mocked OpenAI call returns structured Markdown.<br>✅ Stored in `summaries` table.                                     |
| MVP‑05 | Aggregate between dates | As a user I want summaries between Date‑A and Date‑B so I see everything I missed.                            | ✅ GET `/patches?from=YYYY‑MM‑DD` returns JSON sorted asc.                                                                |
| MVP‑06 | Date‑picker UI          | As a visitor I want to pick the last date I played so the site can show me changes.                           | ✅ Cypress test selects date and shows API results.                                                                       |

## Nice‑to‑have

| ID      | Title                | Description                                                |
| ------- | -------------------- | ---------------------------------------------------------- |
| NICE‑01 | Clipboard share‑link | Click button copies `/since/{date}` to clipboard.          |
| NICE‑02 | Champion filter      | Search box filters accordion to one champion.              |
| NICE‑03 | Dark mode toggle     | Tailwind `dark:` class switch, persists in `localStorage`. |

## Stretch Goals

| ID     | Title             | Description                                                 |
| ------ | ----------------- | ----------------------------------------------------------- |
| STR‑01 | Embeddings search | Ask "When was Katarina nerfed?" powered by pgvector.        |
| STR‑02 | Discord bot       | Slash‑command `/lolpatch since 2025‑01‑01` replies summary. |
| STR‑03 | Change heat‑map   | Visual intensity score per patch based on # of nerfs.       |

---

### Backlog Setup Checklist

- [ ] Create a **GitHub Project** (Board layout).
- [ ] Import each row above as an **Issue** with the label `story/feature`.
- [ ] Add `size/S`, `size/M`, `size/L` labels (t‑shirt sizing).
- [ ] Enable **automated kanban** (`To do` → `In progress` → `Review` → `Done`).
- [ ] Configure branch protection: PR requires passing CI.

---

### Definition of Ready (DoR)

A story is _Ready_ when:

1. Acceptance criteria are concrete and testable.
2. Dependencies identified
3. Test data or fixtures exist.
4. Size label assigned.

---

### Suggested Labels

| Label           | Purpose                           |
| --------------- | --------------------------------- |
| `story/feature` | New functionality                 |
| `story/bug`     | Defect in existing code           |
| `story/chore`   | Non‑user facing work (CI, config) |
| `size/S,M,L`    | Estimate effort                   |
| `priority/high` | Blocks release                    |
