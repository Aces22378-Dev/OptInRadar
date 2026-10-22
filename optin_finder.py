import json
import concurrent.futures
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

def check_single_url(item):
    url = item.get('href')
    title = item.get('title', 'Unknown Title')
    
    if not url or (url.count('/') <= 3 and not any(k in url for k in ['signup', 'join', 'vip', 'text', 'sms', 'club'])):
        return None

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=2.5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text().lower()

            is_free = any(kw in page_text for kw in ['free', 'no cost', 'msg & data rates', 'join for free'])
            has_phone = bool(soup.find('input', {'type': 'tel'})) or any(
                kw in str(inp).lower() for inp in soup.find_all('input') for kw in ['phone', 'mobile', 'sms', 'cell']
            )

            if is_free and has_phone:
                return {"title": title, "url": url}
    except Exception:
        pass
    return None

def main():
    query = '"join our text club" "free" OR "enter your mobile number"'
    print(f"Scanning web for query: {query}")
    
    try:
        results = list(DDGS().text(query, max_results=15))
    except Exception as e:
        print(f"Search error: {e}")
        results = []

    found_matches = []
    if results:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            scan_results = executor.map(check_single_url, results)
            for res in scan_results:
                if res:
                    found_matches.append(res)

    # Save directly to results.json for the website to read
    with open('results.json', 'w') as f:
        json.dump(found_matches, f, indent=2)
    
    print(f"Successfully saved {len(found_matches)} results to results.json")

if __name__ == "__main__":
    main()
