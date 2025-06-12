import requests
import json
from bs4 import BeautifulSoup

def find_patch_version():
    try:
        # Get the latest patch version from the URL
        response = requests.get("https://www.leagueoflegends.com/en-us/news/tags/patch-notes/")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first div with data-testid="card-title" and get the inner text
        latest_patch = soup.find('div', {'data-testid': 'card-title'})
        
        if not latest_patch:
            raise ValueError("Could not find patch version element on page")
        
        # Format correctly for use in URL
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
    # Define the URL for the patch notes
    url = f"https://www.leagueoflegends.com/en-us/news/game-updates/patch-{patch_version}-notes/"
    r = requests.get(url,allow_redirects=True)

    # make patch.html with write binary mode on r.content
    with open(f'patch-{patch_version}.html', 'w', encoding='utf-8') as f:
        f.write(r.text)

def parse_champions(patch_version):
    #TODO: add error handling for file not found or parsing issues
    
    with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find the main content of the patch notes
    champions = {}
    
    # Find the Champions h2 element
    champions_h2 = soup.find('h2', id='patch-champions')
    
    if champions_h2:
        print("Found Champions section")
        # Start from the next sibling after the h2
        current = champions_h2.parent.next_sibling

        # Iterate through siblings until we hit another h2 or header with h2
        while current:
            
            # If we hit another h2 or header with h2, stop
            if current.name == 'h2':
                break
            if current.name == 'header' and current.find('h2'):
                break
            
            # If it's a div with class="content-border", extract h3 and p elements
            if current.name == 'div' and 'content-border' in current.get('class', []):
                # Find h3 with class="change-title"
                change_title = current.find('h3', class_='change-title')
                # Find the summary paragraph - should only be one per div
                summary = current.find('p', class_='summary')
                
                if change_title:
                    # Extract the text from the a tag within the h3
                    title_link = change_title.find('a')
                    title_text = title_link.get_text() if title_link else change_title.get_text()
                    
                    champions[title_text] = summary.get_text() if summary else None
            # Move to the next sibling
            current = current.next_sibling
    
    # Return as JSON object with champions wrapper
    return {"champions": champions}

def parse_items(patch_version):
    

        with open(f'patch-{patch_version}.html', 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

    # Find the main content of the patch notes
    items = {}
    
    # Find the Champions h2 element
    items_h2 = soup.find('h2', id='patch-items')
    
    if items_h2:
        print("Found Items section")
        # Start from the next sibling after the h2
        current = items_h2.parent.next_sibling

        # Iterate through siblings until we hit another h2 or header with h2
        while current:
            
            # If we hit another h2 or header with h2, stop
            if current.name == 'h2':
                break
            if current.name == 'header' and current.find('h2'):
                break
            
            # If it's a div with class="content-border", extract h3 and p elements
            if current.name == 'div' and 'content-border' in current.get('class', []):
                # Find h3 with class="change-detail-title"
                change_title = current.find('h3', class_='change-detail-title')
                # Find the ul element
                ul = current.find('ul')
                
                if change_title and ul:
                    # Extract the text from the h3
                    title_text = change_title.get_text(strip=True)
                    
                    # Extract all li elements text preserving HTML formatting
                    li_items = []
                    for li in ul.find_all('li'):
                        # Get text content
                        li_text = ''
                        for content in li.contents:
                            if hasattr(content, 'get_text'):
                                li_text += content.get_text()
                            else:
                                li_text += str(content)
                        # Replace unicode arrow with ->
                        li_text = li_text.replace('\u21d2', '->')
                        li_items.append(li_text.strip())
                    
                    items[title_text] = li_items
            # Move to the next sibling
            current = current.next_sibling
    else:
        print("No Items section found")
    
    # Return as JSON object with items wrapper
    return {"items": items}

if __name__ == "__main__":
    
    #testing purposes
    patch_version = "25-10"
    #patch_version = find_patch_version()
    print("Found patch:", patch_version)
    
    get_patch(patch_version)

    print("Parsing champions and items from patch notes...")
    print(parse_champions(patch_version))
    print(parse_items(patch_version))

