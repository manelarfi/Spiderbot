# crawler.py
import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import threading
from broken_links import est_broken
from robot_parser import is_allowed

db_path = os.path.join(os.path.dirname(__file__), "crawler.db")

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

def save_url_to_db(url, depth):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute("INSERT OR IGNORE INTO visited_urls (url, depth) VALUES (?, ?)", (url, depth))
        conn.commit()
    finally:
        conn.close()

def crawl(url, visited=None, max_depth=0, depth=0, results=None):
    if visited is None:
        visited = set()
    if results is None:
        results = []

    if url in visited or depth > max_depth:
        return results

    visited.add(url)
    results.append(f"Depth {depth} -> Crawling: {url}")
    save_url_to_db(url, depth)

    if not is_allowed(url):
        results.append(f"[!] Crawling not allowed by robots.txt: {url}")
        return results

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, timeout=5, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            parsed_url = urlparse(full_url)
            if parsed_url.scheme in ["http", "https"] and parsed_url.netloc == urlparse(url).netloc:
                if est_broken(full_url):
                    results.append(f"    [✗] Broken link detected: {full_url}")
                else:
                    results.append(f"    [+] Valid link: {full_url}")
                    links.add(full_url)

        time.sleep(0.5)
        threads = []
        for link in links:
            t = threading.Thread(target=crawl, args=(link, visited, max_depth, depth+1, results))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    except Exception as e:
        results.append(f"[!] Error with {url}: {e}")

    return results

init_db()
