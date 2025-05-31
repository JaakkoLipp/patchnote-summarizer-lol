# Step 6 – Spike / Prototype

_Objective: prove the walking skeleton in ≤ 2 days of coding._ Everything lives under a `/spike` folder so you can throw it away later without polluting `api/` or `web/`.

---

## 6.1 · Deliverables

| What                     | Purpose                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------ |
| **`fetch_patch.py`**     | Download a single patch‑note HTML by URL; save raw file plus metadata JSON.          |
| **`summarise_patch.py`** | Read raw HTML, strip boilerplate, send to OpenAI, print ≤ 6 bullet summary.          |
| **`bootstrap_spike.sh`** | Convenience wrapper to run the two scripts back‑to‑back.                             |
| **`requirements.txt`**   | Minimal deps (`requests`, `beautifulsoup4`, `html2text`, `openai`, `python-dotenv`). |
| **`README_spike.md`**    | 5‑line usage guide + env var setup.                                                  |

---

## 6.2 · Folder Layout

```text
/spike
├─ fetch_patch.py
├─ summarise_patch.py
├─ bootstrap_spike.sh
├─ data/
│   └─ raw_14_10.html
├─ summaries/
│   └─ summary_14_10.md
├─ .env           # OPENAI_API_KEY=...
└─ requirements.txt
```

---

## 6.3 · Example Code Skeletons

### `fetch_patch.py`

```python
#!/usr/bin/env python3
"""Download a single LoL patch‑notes page and save raw HTML + meta."""
import sys, json, pathlib, requests, bs4, datetime as dt
from urllib.parse import urlparse

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.leagueoflegends.com/en-us/news/game-updates/patch-14-10-notes/"
RAW_DIR = pathlib.Path(__file__).parent / "data"
RAW_DIR.mkdir(exist_ok=True)

resp = requests.get(URL, headers={"User-Agent": "LoLPatchSpike/0.1"})
resp.raise_for_status()

slug = urlparse(URL).path.strip('/').split('/')[-1]
html_path = RAW_DIR / f"{slug}.html"
html_path.write_text(resp.text, encoding="utf-8")

meta = {
    "url": URL,
    "fetched_at": dt.datetime.utcnow().isoformat(),
    "bytes": len(resp.content),
}
(json_path := html_path.with_suffix('.json')).write_text(json.dumps(meta, indent=2))
print(f"Saved {html_path} and {json_path}")
```

### `summarise_patch.py`

```python
#!/usr/bin/env python3
"""Strip article to plain text and summarise with OpenAI."""
import sys, pathlib, os, openai, bs4, html2text, re

RAW_FILE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "data/patch-14-10-notes.html"
openai.api_key = os.getenv("OPENAI_API_KEY")

html = RAW_FILE.read_text()
article = bs4.BeautifulSoup(html, "html.parser").select_one("article[data-testid=story-container]")
text_md = html2text.HTML2Text().handle(str(article))

prompt = (
    "You are an esports analyst. Summarise the following League of Legends patch section in no more than 6 bullet points. "
    "Mark each point with ✅ buff, ❌ nerf, or ✨ adjust.\n\n" + text_md[:2000]
)
response = openai.chat.completions.create(
    model="gpt-4o-mini",  # cheapest model for spike
    messages=[{"role": "system", "content": prompt}],
)
summary = response.choices[0].message.content.strip()

OUT_DIR = pathlib.Path(__file__).parent / "summaries"
OUT_DIR.mkdir(exist_ok=True)
(out_file := OUT_DIR / f"summary_{RAW_FILE.stem}.md").write_text(summary)
print(f"Summary saved to {out_file}\n---\n{summary}")
```

_Replace `gpt-4o-mini` with the model you have access to._

---

## 6.4 · Run It

```bash
cd spike
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
./fetch_patch.py https://www.leagueoflegends.com/en-us/news/game-updates/patch-14-10-notes/
./summarise_patch.py data/patch-14-10-notes.html
```

---

## 6.5 · Success Criteria

- [ ] Raw HTML file exists and > 10 KB.
- [ ] Summary file < 1 KB and has ≤ 6 bullet points.
- [ ] Scripts exit with code 0.

---

## 6.6 · Next After Spike

1. **Move code** into `api/services/patch_notes/` folder.
2. Swap out env‑var wiring for `pydantic` settings.
3. Add unit tests around `clean_html()` and `summarise_section()`.
4. Wire into FastAPI route `/patches`.

---

> _Edit anything—change URLs, filenames, or dependencies—then we’ll refine or migrate to production code._
