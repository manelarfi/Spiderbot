import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import threading
from robot_parser import is_allowed  # Import the is_allowed function

def crawl(url, visited=None, max_depth=2, depth=0):
    if visited is None:
        visited = set()

    if url in visited or depth > max_depth:
        return

    visited.add(url)
    print(f"[*] Depth {depth} -> Crawling: {url}")

    # Check if the website allows crawling based on robots.txt
    if not is_allowed(url):
        print(f"[!] Crawling not allowed by robots.txt: {url}")
        return
    else:
        print("acces granted hbb")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, timeout=5, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.scheme in ["http", "https"] and parsed_url.netloc == urlparse(url).netloc:
                links.add(full_url)
                print(f"    [+] Found: {full_url}")

        time.sleep(0.5)  # To avoid overwhelming the server
        threads = []
        for link in links:
            thread = threading.Thread(target=crawl, args=(link, visited, max_depth, depth + 1))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error with {url}: {e}")
    except Exception as e:
        print(f"[!] Unexpected error: {e}")

if __name__ == "__main__":
    start_url = input("Enter the URL to start crawling from (format should be : https://example.com): ")
    crawl(start_url)
    print("Crawling completed.")
