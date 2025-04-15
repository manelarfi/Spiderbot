import urllib.robotparser
from urllib.parse import urlparse

def is_allowed(url, user_agent="*"):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url + "/robots.txt")

    try:
        rp.read()
    except Exception as e:
        print(f"[!] Couldn't read robots.txt: {e}")
        return False  # Default to disallow if robots.txt can't be read

    return rp.can_fetch(user_agent, url)
