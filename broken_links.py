import requests

def est_broken(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code >= 400
    except requests.RequestException:
        return True


