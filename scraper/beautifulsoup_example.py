from bs4 import BeautifulSoup
import json
import re

def parse_patch_notes_to_json(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # First, try to extract JSON data from __NEXT_DATA__ script tag
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    if script_tag:
        try:
            json_data = json.loads(script_tag.string)
            # Navigate to the rich text content
            blades = json_data['props']['pageProps']['page']['blades']
            
            patch_data = {
                "champions": [],
                "items": [],
                "aram": [],
                "brawl": [],
                "general": []
            }
            
            # Find the patch notes rich text blade
            for blade in blades:
                if blade.get('type') == 'patchNotesRichText':
                    rich_text = blade.get('richText', {})
                    # Parse the rich text structure here
                    patch_data = parse_rich_text_content(rich_text)
                    break
            
            return patch_data
            
        except json.JSONDecodeError:
            print("Failed to parse JSON from script tag")
    
    # Fallback: Parse HTML structure directly (your original approach)
    return parse_html_structure(soup)

def parse_rich_text_content(rich_text):
    """Parse the rich text content from the JSON structure"""
    patch_data = {
        "champions": [],
        "items": [],
        "aram": [],
        "brawl": [],
        "general": []
    }
    
    # The rich text content will be in a nested structure
    # You'll need to examine the actual JSON structure to parse this correctly
    # This is just a template - you'll need to adapt based on the actual structure
    
    return patch_data

def parse_html_structure(soup):
    """Your original HTML parsing approach as fallback"""
    patch_data = {
        "champions": [],
        "items": [],
        "aram": [],
        "brawl": [],
        "general": []
    }
    
    # Find champion changes
    champion_blocks = soup.find_all('div', class_='patch-change-block')
    
    for block in champion_blocks:
        # Get champion name from the h3 tag
        champion_name_elem = block.find('h3', class_='change-title')
        if not champion_name_elem:
            continue
            
        champion_name = champion_name_elem.get_text(strip=True)
        
        # Get summary
        summary_elem = block.find('p', class_='summary')
        summary = summary_elem.get_text(strip=True) if summary_elem else ""
        
        # Get context (the reasoning)
        context_elem = block.find('blockquote', class_='blockquote context')
        context = context_elem.get_text(strip=True) if context_elem else ""
        
        # Get ability changes
        abilities = []
        ability_sections = block.find_all('h4', class_='change-detail-title ability-title')
        
        for ability in ability_sections:
            ability_name = ability.get_text(strip=True)
            
            # Find the next ul element for changes
            changes_list = ability.find_next_sibling('ul')
            changes = []
            if changes_list:
                for li in changes_list.find_all('li'):
                    changes.append(li.get_text(strip=True))
            
            abilities.append({
                "name": ability_name,
                "changes": changes
            })
        
        # Get base stat changes
        base_stats = []
        base_stat_section = block.find('h4', string='Base Stats')
        if base_stat_section:
            stats_list = base_stat_section.find_next_sibling('ul')
            if stats_list:
                for li in stats_list.find_all('li'):
                    base_stats.append(li.get_text(strip=True))
        
        champion_data = {
            "name": champion_name,
            "summary": summary,
            "context": context,
            "abilities": abilities,
            "base_stats": base_stats
        }
        
        patch_data["champions"].append(champion_data)
    
    # Add parsing for items, ARAM, etc. using similar patterns
    # Look for sections with different class names or IDs
    
    return patch_data

# Example usage
if __name__ == "__main__":
    # Read your HTML file
    with open('patch.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse to JSON
    patch_json = parse_patch_notes_to_json(html_content)
    
    # Save to file
    with open('patch_data.json', 'w', encoding='utf-8') as file:
        json.dump(patch_json, file, indent=2, ensure_ascii=False)
    
    print(f"Extracted {len(patch_json['champions'])} champions")
    print(f"Extracted {len(patch_json['items'])} items")
    print(f"Extracted {len(patch_json['aram'])} ARAM changes")
    print(f"Extracted {len(patch_json['brawl'])} brawl changes")