import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
from io import BytesIO
from PIL import Image
from filestack import Client


FILESTACK_API_KEY = 'Abnq7E6rVRaiHd14Jibe8z'
SCREENSHOTLAYER_API_KEY = '82f593d3be17d04f8e66b36f10e07dba'
SCREENSHOTLAYER_API_URL = 'https://api.savepage.io/v1/'


def get_website_title(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    only_head = SoupStrainer('head')
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser', parse_only=only_head)
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


def create_website_thumbnail_image(url):
    payload = {
        'key': SCREENSHOTLAYER_API_KEY,
        'q': url
    }

    response = requests.get(SCREENSHOTLAYER_API_URL, params=payload)
    im = Image.open(BytesIO(response.content))
    im.thumbnail((250, 156))
    im.save('thumbnail.png')


def get_website_thumbnail_url():
    client = Client(FILESTACK_API_KEY)
    file = client.upload(filepath='thumbnail.png')

    return file.url


def generate_website_thumbnail(url):
    create_website_thumbnail_image(url)
    return get_website_thumbnail_url()
