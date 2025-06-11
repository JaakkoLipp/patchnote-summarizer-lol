import requests
import json
from bs4 import BeautifulSoup

# get patchnote
url = "https://www.leagueoflegends.com/en-us/news/game-updates/patch-25-11-notes/"

def get_patch(url):
    r = requests.get(url,allow_redirects=True)

    # make patch.html with write binary mode on r.content
    open('patch.html', 'wb').write(r.content)

def parse_to_json():
    with open('patch.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    patch_data = {
        "title": soup.find('h1').text.strip(),
        "date": soup.find('time').text.strip(),
        "content": []
    }

    for section in soup.find_all('section'):
        section_title = section.find('h2')
        if section_title:
            patch_data["content"].append({
                "section_title": section_title.text.strip(),
                "items": []
            })
            for item in section.find_all('li'):
                patch_data["content"][-1]["items"].append(item.text.strip())

    with open('patch.json', 'w', encoding='utf-8') as json_file:
        json.dump(patch_data, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    print("league patchnote scraped successfully")
    get_patch(url)
    parse_to_json()
