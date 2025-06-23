import requests
import json
from bs4 import BeautifulSoup

# Constants
BASE_URL = "https://www.leagueoflegends.com/en-us"
PATCH_NOTES_URL = f"{BASE_URL}/news/tags/patch-notes/"
PATCH_DETAIL_URL = f"{BASE_URL}/news/game-updates/patch-{{version}}-notes/"


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
        if not patch_text or ' ' not in patch_text:
            raise ValueError("Invalid patch version format found")
            
        latest_patch = patch_text.split(' ')[1].replace('.', '-')
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


def get_patch(patch_version):
    """Download patch notes HTML and save to file."""
    url = PATCH_DETAIL_URL.format(version=patch_version)
    r = requests.get(url, allow_redirects=True)

    with open(f'patch-{patch_version}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)


def parse_champions(patch_version):
    """Parse champion changes from the patch notes."""
    try:
        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        champions = {}
        champions_h2 = soup.find('h2', id='patch-champions')
        
        if champions_h2:
            print("Found Champions section")
            current = champions_h2.parent.next_sibling

            while current:
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break
                
                if current.name == 'div' and 'content-border' in current.get('class', []):
                    change_title = current.find('h3', class_='change-title')
                    summary = current.find('p', class_='summary')
                    
                    if change_title:
                        title_link = change_title.find('a')
                        title_text = title_link.get_text() if title_link else change_title.get_text()
                        champions[title_text] = summary.get_text() if summary else None
                
                current = current.next_sibling
        
        return {"champions": champions}
    except FileNotFoundError:
        print(f"Error: patch-{patch_version}.html file not found")
        return {"champions": {}}
    except Exception as e:
        print(f"Error parsing champions: {e}")
        return {"champions": {}}


def parse_items(patch_version):
    """Parse item changes from the patch notes."""
    try:
        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        items = {}
        items_h2 = soup.find('h2', id='patch-items')
        
        if items_h2:
            print("Found Items section")
            current = items_h2.parent.next_sibling

            while current:
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break
                
                if current.name == 'div' and 'content-border' in current.get('class', []):
                    change_title = current.find('h3', class_='change-detail-title')
                    ul = current.find('ul')
                    
                    if change_title and ul:
                        title_text = change_title.get_text(strip=True)
                        
                        li_items = []
                        for li in ul.find_all('li'):
                            li_text = ''
                            for content in li.contents:
                                if hasattr(content, 'get_text'):
                                    li_text += content.get_text()
                                else:
                                    li_text += str(content)
                            li_text = li_text.replace('\u21d2', '->')
                            li_items.append(li_text.strip())
                        
                        items[title_text] = li_items
                
                current = current.next_sibling
        else:
            print("No Items section found")
        
        return {"items": items}
    except FileNotFoundError:
        print(f"Error: patch-{patch_version}.html file not found")
        return {"items": {}}
    except Exception as e:
        print(f"Error parsing items: {e}")
        return {"items": {}}


def parse_other(patch_version):
    """Parse all other sections from the patch notes."""
    try:
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
            current = h2.parent.next_sibling
            
            while current:
                if current.name == 'h2' or (current.name == 'header' and current.find('h2')):
                    break
                
                if current.name == 'div' and 'content-border' in current.get('class', []):
                    change_title = current.find(['h3', 'h4'], class_=['change-title', 'change-detail-title'])
                    blockquote = current.find('blockquote', class_='blockquote')
                    
                    if blockquote:
                        blockquote_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                               for content in blockquote.contents)
                        
                        if not content_json[section_key]:
                            content_json[section_key] = {'content': blockquote_text.strip()}
                        elif isinstance(content_json[section_key], dict):
                            content_json[section_key]['note'] = blockquote_text.strip()
                        else:
                            content_json[section_key] = {
                                'content': content_json[section_key],
                                'note': blockquote_text.strip()
                            }
                    
                    elif change_title:
                        title_link = change_title.find('a')
                        title_text = title_link.get_text(strip=True) if title_link else change_title.get_text(strip=True)
                        
                        summary = current.find('p', class_='summary')
                        ul = current.find('ul')
                        
                        if summary:
                            content_json[section_key][title_text] = summary.get_text(strip=True)
                        elif ul:
                            li_items = []
                            for li in ul.find_all('li'):
                                li_text = ''.join(str(content.get_text() if hasattr(content, 'get_text') else content)
                                              for content in li.contents)
                                li_items.append(li_text.replace('\u21d2', '->').strip())
                            content_json[section_key][title_text] = li_items
                        else:
                            content_json[section_key][title_text] = "Content available but not parsed"
                
                current = current.next_sibling

            if isinstance(content_json.get(section_key), dict) and not content_json[section_key]:
                del content_json[section_key]
        
        print(f"Parsed {len(content_json)} sections from patch notes")
        return content_json
    except FileNotFoundError:
        print(f"Error: patch-{patch_version}.html file not found")
        return {}
    except Exception as e:
        print(f"Error parsing other sections: {e}")
        return {}


if __name__ == "__main__":
    patch_version = find_patch_version()
    print("Found patch:", patch_version)
    
    get_patch(patch_version)

    champions_data = parse_champions(patch_version)
    items_data = parse_items(patch_version)
    other_data = parse_other(patch_version)
    
    print("Champions (pretty printed):")
    print(json.dumps(champions_data, indent=2, ensure_ascii=False))
    
    print("\nItems (pretty printed):")
    print(json.dumps(items_data, indent=2, ensure_ascii=False))
    
    print("\nOther changes (pretty printed):")
    print(json.dumps(other_data, indent=2, ensure_ascii=False))
