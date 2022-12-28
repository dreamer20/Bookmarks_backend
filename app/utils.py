import requests
import re
from bs4 import BeautifulSoup


def get_website_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string
    except Exception:
        title = 'Bookmark Title'

    return title


def get_website_icon_url(url):
    match = re.match(r'^http(s?)://(.+?)([^/]+)', url)
    root = match.group(0)

    return root + '/favicon.ico'


def is_valid_url(url):
    match = re.match(r'^http(s?)://.*', url)
    if match:
        return True
    return False
