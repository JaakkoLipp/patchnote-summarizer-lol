import requests
import json
import re
from bs4 import BeautifulSoup
import os

# Constants
BASE_URL = "https://www.leagueoflegends.com/en-us"
PATCH_NOTES_URL = f"{BASE_URL}/news/tags/patch-notes/"
PATCH_DETAIL_URL = f"{BASE_URL}/news/game-updates/patch-{{version}}-notes/"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://65.21.183.21:2556")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi4-mini")


def find_patch_version():
    """Find the latest patch version from the League of Legends website."""
    try:
        response = requests.get(PATCH_NOTES_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        latest_patch = soup.find('div', {'data-testid': 'card-title'})
        
        if not latest_patch:
            raise ValueError("Could not find patch version element on page")
        
        patch_text = latest_patch.get_text(strip=True)
        if not patch_text:
            raise ValueError("Invalid patch version format found")

        # Prefer explicit version pattern like 25.14; fall back to splitting text
        m = re.search(r"(\d+\.\d+)", patch_text)
        if m:
            latest_patch = m.group(1).replace('.', '-')
        else:
            parts = patch_text.split()
            if len(parts) >= 2:
                latest_patch = parts[1].replace('.', '-')
            else:
                raise ValueError("Could not determine patch version from text")
        
        # check if the patch file already exists
        filename = f'patch-{latest_patch}.html'
        if not os.path.exists(filename):
            print(f"{filename} not found; downloading patch HTML...")
            try:
                get_patch(latest_patch)
            except Exception as e:
                print(f"Failed to download patch file: {e}")
        
        return latest_patch
    except requests.exceptions.RequestException as e:
        print(f"Error fetching patch notes page: {e}")
        return None
    except (ValueError, IndexError) as e:
        print(f"Error parsing patch version: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


# Simple in-memory cache for parsed bundle per version
_BUNDLE_CACHE: dict[str, dict] = {}


def get_patch(patch_version):
    """Download patch notes HTML and save to file."""
    if not patch_version:
        raise ValueError("patch_version is required to download patch HTML")

    url = PATCH_DETAIL_URL.format(version=patch_version)
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()

    with open(f'patch-{patch_version}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)


def list_patch_versions(limit: int = 3):
    """Return the last N patch versions as dashed strings, e.g., ["25-16", "25-15", ...]."""
    try:
        response = requests.get(PATCH_NOTES_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        versions = []
        seen = set()

        for title_div in soup.find_all('div', attrs={'data-testid': 'card-title'}):
            text = title_div.get_text(strip=True)
            if not text:
                continue
            m = re.search(r"(\d+\.\d+)", text)
            if not m:
                continue
            dotted = m.group(1)
            dashed = dotted.replace('.', '-')
            if dashed in seen:
                continue
            seen.add(dashed)
            versions.append(dashed)
            if len(versions) >= max(1, int(limit)):
                break

        return {"versions": versions}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching versions: {e}")
        return {"versions": []}
    except Exception as e:
        print(f"Unexpected error in list_patch_versions: {e}")
        return {"versions": []}


def _ensure_patch_file(patch_version):
    """Ensure the patch HTML file exists; download it if missing. Returns True if file exists."""
    filename = f'patch-{patch_version}.html'
    if not os.path.exists(filename):
        try:
            print(f"{filename} not found; downloading patch HTML...")
            get_patch(patch_version)
        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            return False
    return os.path.exists(filename)


def parse_champions(patch_version):
    """Parse champion changes from the patch notes."""
    try:
        if not patch_version:
            print("No patch_version provided to parse_champions")
            return {"champions": {}}

        if not _ensure_patch_file(patch_version):
            return {"champions": {}}
        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        champions = {}
        champions_h2 = soup.find('h2', id='patch-champions')
        
        if champions_h2:
            print("Found Champions section")
            current = champions_h2.parent.find_next_sibling()

            while current:
                # stop when next major section (another h2) is reached
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break

                if current.name == 'div' and 'content-border' in current.get('class', []):
                    change_title = current.find(['h3', 'h4'], class_=['change-title', 'change-detail-title'])
                    summary = current.find('p', class_='summary')

                    if change_title:
                        title_link = change_title.find('a')
                        title_text = title_link.get_text(strip=True) if title_link else change_title.get_text(strip=True)
                        champions[title_text] = summary.get_text(strip=True) if summary else None

                current = current.find_next_sibling()
        
        return {"champions": champions}
    except Exception as e:
        print(f"Error parsing champions: {e}")
        return {"champions": {}}


def parse_items(patch_version):
    """Parse item changes from the patch notes."""
    try:
        if not patch_version:
            print("No patch_version provided to parse_items")
            return {"items": {}}

        if not _ensure_patch_file(patch_version):
            return {"items": {}}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        items = {}
        items_h2 = soup.find('h2', id='patch-items')

        if items_h2:
            print("Found Items section")
            current = items_h2.parent.find_next_sibling()  # skip text nodes

            while current:
                # stop once next major section starts
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break

                if current.name == 'div' and 'content-border' in current.get('class', []):
                    # item titles in the patch HTML use either "change-title" or "change-detail-title"
                    change_title = current.find(['h3', 'h4'], class_=['change-title', 'change-detail-title'])
                    ul = current.find('ul')

                    if change_title and ul:
                        title_text = change_title.get_text(strip=True)

                        li_items = []
                        for li in ul.find_all('li'):
                            li_text_parts = []
                            for content in li.contents:
                                if hasattr(content, 'get_text'):
                                    li_text_parts.append(content.get_text())
                                else:
                                    li_text_parts.append(str(content))
                            li_text = ''.join(li_text_parts).replace('\u21d2', '->').strip()
                            li_items.append(li_text)

                        items[title_text] = li_items

                current = current.find_next_sibling()

        else:
            print("No Items section found")

        return {"items": items}
    except Exception as e:
        print(f"Error parsing items: {e}")
        return {"items": {}}

def parse_other(patch_version):
    """Parse all other sections from the patch notes."""
    try:
        if not patch_version:
            print("No patch_version provided to parse_other")
            return {}

        if not _ensure_patch_file(patch_version):
            return {}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        content_json = {}
        headings = soup.find_all('h2')

        for h2 in headings:
            heading_text = h2.get_text(strip=True)

            if heading_text.lower() in ['champions', 'items']:
                continue

            section_key = h2.get('id', '').replace('patch-', '') or heading_text.lower()

            if h2.get('id', '') == 'patch-patch-highlights':
                highlights_div = h2.parent.find_next_sibling('div', class_='content-border')
                if highlights_div and (p_tag := highlights_div.find('p')):
                    content_json[section_key] = p_tag.get_text(strip=True)
                    continue

            content_json[section_key] = {}
            current = h2.parent.find_next_sibling()

            while current:
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break

                if current.name == 'div' and 'content-border' in current.get('class', []):
                    change_title = current.find(['h3', 'h4'], class_=['change-title', 'change-detail-title'])
                    blockquote = current.find('blockquote', class_='blockquote')

                    # When a title exists, capture content under that title
                    if change_title:
                        title_link = change_title.find('a')
                        title_text = title_link.get_text(strip=True) if title_link else change_title.get_text(strip=True)

                        summary = current.find('p', class_='summary')
                        ul = current.find('ul')

                        entry = None
                        if summary:
                            entry = summary.get_text(strip=True)
                        elif ul:
                            li_items = []
                            for li in ul.find_all('li'):
                                li_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                              for content in li.contents)
                                li_items.append(li_text.replace('\u21d2', '->').strip())
                            entry = li_items
                        else:
                            entry = "Content available but not parsed"

                        # Attach blockquote as note to this entry if present
                        if blockquote:
                            blockquote_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                                   for content in blockquote.contents).strip()
                            if isinstance(entry, dict):
                                entry['note'] = blockquote_text
                            else:
                                entry = { 'content': entry, 'note': blockquote_text }

                        content_json[section_key][title_text] = entry

                    # If no title but a blockquote exists, store it as a section-level note
                    elif blockquote:
                        blockquote_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                               for content in blockquote.contents).strip()
                        content_json[section_key].setdefault('notes', []).append(blockquote_text)

                current = current.find_next_sibling()

            if isinstance(content_json.get(section_key), dict) and not content_json[section_key]:
                del content_json[section_key]

        print(f"Parsed {len(content_json)} sections from patch notes")
        return content_json
    except Exception as e:
        print(f"Error parsing other sections: {e}")
        return {}


def parse_arena(patch_version):
    """Parse Arena-specific changes from the patch notes. Returns {"arena": {...}}"""
    try:
        if not patch_version:
            print("No patch_version provided to parse_arena")
            return {"arena": {}}

        if not _ensure_patch_file(patch_version):
            return {"arena": {}}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Find an H2 whose id or text contains 'arena'
        arena_h2 = None
        for h2 in soup.find_all('h2'):
            htxt = h2.get_text(strip=True).lower()
            hid = (h2.get('id') or '').lower()
            if 'arena' in htxt or 'arena' in hid:
                arena_h2 = h2
                break

        if not arena_h2:
            print("No Arena section found")
            return {"arena": {}}

        arena_json = {}
        current = arena_h2.parent.find_next_sibling()

        while current:
            if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                break

            if current.name == 'div' and 'content-border' in current.get('class', []):
                change_title = current.find(['h3', 'h4'], class_=['change-title', 'change-detail-title'])
                blockquote = current.find('blockquote', class_='blockquote')

                if change_title:
                    title_link = change_title.find('a')
                    title_text = title_link.get_text(strip=True) if title_link else change_title.get_text(strip=True)

                    summary = current.find('p', class_='summary')
                    ul = current.find('ul')

                    entry = None
                    if summary:
                        entry = summary.get_text(strip=True)
                    elif ul:
                        li_items = []
                        for li in ul.find_all('li'):
                            li_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                              for content in li.contents)
                            li_items.append(li_text.replace('\u21d2', '->').strip())
                        entry = li_items
                    else:
                        entry = "Content available but not parsed"

                    if blockquote:
                        note_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                            for content in blockquote.contents).strip()
                        if isinstance(entry, dict):
                            entry['note'] = note_text
                        else:
                            entry = { 'content': entry, 'note': note_text }

                    arena_json[title_text] = entry

                elif blockquote:
                    note_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                        for content in blockquote.contents).strip()
                    if note_text:
                        arena_json.setdefault('notes', []).append(note_text)

            current = current.find_next_sibling()

        return {"arena": arena_json}
    except Exception as e:
        print(f"Error parsing arena section: {e}")
        return {"arena": {}}


def collect_arena_everywhere(patch_version):
    """Scan the entire document for 'arena' mentions and return context snippets.

    Returns {"arena_mentions": [{"context": <where>, "text": <text>}, ...]}
    """
    try:
        if not patch_version:
            print("No patch_version provided to collect_arena_everywhere")
            return {"arena_mentions": []}

        if not _ensure_patch_file(patch_version):
            return {"arena_mentions": []}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        mentions = []
        seen = set()

        def add(ctx, text):
            if not text:
                return
            t = ' '.join(text.split())
            if 'arena' in t.lower() and t not in seen:
                seen.add(t)
                mentions.append({"context": ctx, "text": t})

        for h2 in soup.find_all('h2'):
            add('h2', h2.get_text(' ', strip=True))

        for change in soup.find_all(['h3', 'h4']):
            add('change_title', change.get_text(' ', strip=True))
            parent = change.find_parent('div')
            if parent:
                summary = parent.find('p', class_='summary')
                if summary:
                    add('summary', summary.get_text(' ', strip=True))
                for li in parent.find_all('li'):
                    add('li', li.get_text(' ', strip=True))

        for p in soup.find_all('p'):
            add('p', p.get_text(' ', strip=True))

        return {"arena_mentions": mentions}
    except Exception as e:
        print(f"Error collecting arena mentions: {e}")
        return {"arena_mentions": []}


def parse_tagline(patch_version: str):
    """Extract the short developer tagline/summary from the patch HTML.

    Looks for the element with data-testid="tagline" first. If missing, falls back to
    meta description or og:description. Returns {"tagline": <str or None>}.
    """
    try:
        if not patch_version:
            print("No patch_version provided to parse_tagline")
            return {"tagline": None}

        if not _ensure_patch_file(patch_version):
            return {"tagline": None}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Primary: explicit tagline block on page body
        tag_div = soup.find('div', attrs={'data-testid': 'tagline'})
        if tag_div:
            text = tag_div.get_text(" ", strip=True)
            if text:
                return {"tagline": text}

        # Fallbacks: meta description or og:description in head
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return {"tagline": meta_desc.get('content')}

        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return {"tagline": og_desc.get('content')}

        return {"tagline": None}
    except Exception as e:
        print(f"Error parsing tagline: {e}")
        return {"tagline": None}


def parse_highlights(patch_version: str):
    """Extract Patch Highlights hero image (and caption if present).

    Returns {"highlights": {"image": str|None, "alt": str, "caption": str}}
    """
    try:
        if not patch_version:
            print("No patch_version provided to parse_highlights")
            return {"highlights": {"image": None, "alt": "", "caption": ""}}

        if not _ensure_patch_file(patch_version):
            return {"highlights": {"image": None, "alt": "", "caption": ""}}

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Locate the Patch Highlights section (by id or text)
        target_h2 = None
        for h2 in soup.find_all('h2'):
            hid = (h2.get('id') or '').lower()
            htxt = h2.get_text(strip=True).lower()
            if hid == 'patch-patch-highlights' or 'patch highlights' in htxt:
                target_h2 = h2
                break

        result = {"image": None, "alt": "", "caption": ""}
        if not target_h2:
            return {"highlights": result}

        # The content is typically in the next sibling content-border div
        content = target_h2.parent.find_next_sibling('div', class_='content-border')
        if not content:
            content = target_h2.find_next('div', class_='content-border')

        if content:
            # Try to find an <img> or <source> inside a <picture>
            img = content.find('img')
            if img and (img.get('src') or img.get('data-src') or img.get('srcset')):
                src = img.get('src') or img.get('data-src')
                if not src and img.get('srcset'):
                    # pick first URL in srcset
                    src = (img.get('srcset').split(',')[0] or '').strip().split(' ')[0]
                result['image'] = src
                result['alt'] = img.get('alt') or ''
            else:
                # Look for <source srcset="..."> within a picture
                source = content.find('source')
                if source and source.get('srcset'):
                    src = (source.get('srcset').split(',')[0] or '').strip().split(' ')[0]
                    result['image'] = src
                    result['alt'] = ''

            # Optional caption: first <p> text in this block
            p = content.find('p')
            if p:
                result['caption'] = p.get_text(' ', strip=True)

        return {"highlights": result}
    except Exception as e:
        print(f"Error parsing highlights: {e}")
        return {"highlights": {"image": None, "alt": "", "caption": ""}}


def get_bundle(patch_version: str) -> dict:
    """Aggregate all parsed data for a version, with simple caching."""
    if not patch_version:
        return {}
    if patch_version in _BUNDLE_CACHE:
        return _BUNDLE_CACHE[patch_version]

    # Ensure HTML exists (parsers already call this, but cheap double-check)
    _ensure_patch_file(patch_version)

    champs = parse_champions(patch_version).get("champions", {})
    items = parse_items(patch_version).get("items", {})
    other = parse_other(patch_version)
    arena = parse_arena(patch_version).get("arena", {})
    mentions = collect_arena_everywhere(patch_version).get("arena_mentions", [])
    tagline = parse_tagline(patch_version).get("tagline")
    highlights = parse_highlights(patch_version).get("highlights", {"image": None, "alt": "", "caption": ""})

    bundle = {
        "version": patch_version,
        "champions": champs,
        "items": items,
        "other": other,
        "arena": {"arena": arena, "mentions": mentions},
        "tagline": tagline,
        "highlights": highlights,
    }
    _BUNDLE_CACHE[patch_version] = bundle
    return bundle


def generate_one_liner_summary(patch_version: str):
    """Generate a concise one-liner summary of changes using an Ollama LLM.

    Returns {"summary": str | None, "error": Optional[str]}
    """
    try:
        if not patch_version:
            return {"summary": None, "error": "missing patch_version"}

        # small context: concise snippets from champions/items plus section names (no tagline)
        champs_dict = parse_champions(patch_version).get("champions", {})
        items_dict = parse_items(patch_version).get("items", {})
        other_sections = list(parse_other(patch_version).keys())

        # Champion samples (up to 3): "Brand — Passive damage to monsters increased; Q stun duration increased; R cooldown decreased."
        champ_samples = []
        for i, (name, summary) in enumerate(champs_dict.items()):
            if i >= 3:
                break
            if summary:
                champ_samples.append(f"{name} — {summary}")
            else:
                champ_samples.append(f"{name}")
        champ_samples_str = " | ".join(champ_samples)

        # Item samples (up to 2), each with up to 2 concise bullets
        item_samples = []
        for j, (iname, bullets) in enumerate(items_dict.items()):
            if j >= 2:
                break
            if isinstance(bullets, list) and bullets:
                joined = "; ".join(str(b).strip() for b in bullets[:2])
                item_samples.append(f"{iname} — {joined}")
            else:
                item_samples.append(f"{iname}")
        item_samples_str = " | ".join(item_samples)

        sections_str = ", ".join(other_sections[:4])

        prompt = (
            "You are an expert League of Legends patch analyst. "
            "Write ONE concise sentence (max 22 words) for PLAYERS. "
            "Prioritize the 1–3 most impactful shifts: major champion buffs/nerfs, item or system changes, or mode updates (e.g., Arena). "
            "Prefer naming specific champions/items/modes; avoid stats, raw numbers, lists, and minor fixes. "
            "Do not use vague abstractions like ‘crowd control’ when specifics exist; prefer paraphrases like ‘longer stuns’, ‘faster clears’, ‘shorter cooldowns’. "
            "Use active voice; no intro text, no quotes, no parentheses; at most one semicolon; end with a period. "
            "If nothing stands out, say ‘Minor balance and quality-of-life tweaks.’\n\n"
            f"Champion changes (sample): {champ_samples_str if champ_samples_str else 'None'}\n"
            f"Item changes (sample): {item_samples_str if item_samples_str else 'None'}\n"
            f"Other sections (sample): {sections_str if sections_str else 'None'}\n\n"
            "Return only the single sentence."
        )

        url = f"{OLLAMA_URL.rstrip('/')}/api/generate"
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        # Common Ollama /api/generate response contains 'response'
        text = data.get("response") or data.get("message") or None
        if text:
            # normalize whitespace and enforce single sentence + <= 22 words
            one = " ".join(str(text).strip().split())
            # take first line only
            one = one.split("\n", 1)[0].strip()
            words = one.split()
            if len(words) > 22:
                one = " ".join(words[:22]).rstrip(",;:") + "."
            # ensure trailing period
            if not one.endswith(('.', '!', '?')):
                one = one.rstrip(",;:") + "."
            return {"summary": one}
        return {"summary": None, "error": "no response text"}
    except requests.exceptions.RequestException as e:
        return {"summary": None, "error": f"ollama request failed: {e}"}
    except Exception as e:
        return {"summary": None, "error": str(e)}


if __name__ == "__main__":
    pv = find_patch_version()
    print("Found patch:", pv)

    get_patch(pv)

    champions_data = parse_champions(pv)
    items_data = parse_items(pv)
    other_data = parse_other(pv)

    print("Champions (pretty printed):")
    # print(json.dumps(champions_data, indent=2, ensure_ascii=False))

    print("\nItems (pretty printed):")
    print(json.dumps(items_data, indent=2, ensure_ascii=False))

    print("\nOther changes (pretty printed):")
    # print(json.dumps(other_data, indent=2, ensure_ascii=False))
