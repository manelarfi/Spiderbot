import os
import sqlite3
import time
import threading
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from robot_parser import is_allowed
from broken_links import est_broken

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

# Setup path to DB
db_path = os.path.join(os.path.dirname(__file__), "crawler.db")

# Initialize DB
def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visited_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            depth INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Base de données 'crawler.db' créée avec succès.")

# Save visited URL
def save_url_to_db(url, depth):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO visited_urls (url, depth) VALUES (?, ?)", (url, depth))
        conn.commit()
    except sqlite3.Error as e:
        print(f"[!] Erreur DB : {e}")
    finally:
        conn.close()

# Get JavaScript-rendered HTML using Selenium
def get_rendered_html(url):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--log-level=3')  # suppress warnings
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)
        driver.get(url)
        time.sleep(2)  # wait for JS to render
        html = driver.page_source
        driver.quit()
        return html
    except WebDriverException as e:
        print(f"[!] Selenium error: {e}")
        return None

# Recursive crawler
def crawl(url, visited=None, max_depth=0, depth=0):
    if visited is None:
        visited = set()

    if url in visited or depth > max_depth:
        return

    visited.add(url)
    print(f"[*] Depth {depth} -> Crawling: {url}")

    if not is_allowed(url):
        print(f"[!] Crawling not allowed by robots.txt: {url}")
        return
    else:
        print("✅ Access granted by robots.txt.")

    try:
        
        html = get_rendered_html(url)
        if not html:
            print("RANI HNAAA")
            return

        soup = BeautifulSoup(html, "html.parser")
        
        links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)

            if parsed_url.scheme in ["http", "https"] and parsed_url.netloc == urlparse(url).netloc:
                if est_broken(full_url):
                    print(f"    [✗] Broken link detected: {full_url}")
                else:
                    print(f"    [+] Valid link: {full_url}")
                    links.add(full_url)

        save_url_to_db(url, depth)
        time.sleep(0.5)

        threads = []
        for link in links:
            thread = threading.Thread(target=crawl, args=(link, visited, max_depth, depth + 1))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except Exception as e:
        print(f"[!] Unexpected error while crawling {url}: {e}")

# Main
init_db()

if __name__ == "__main__":
    start_url = input("Enter the URL to start crawling from (format should be: https://example.com): ")
    crawl(start_url)
    print("Crawling completed.")
