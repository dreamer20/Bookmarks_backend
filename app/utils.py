import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
from io import BytesIO
from PIL import Image
from filestack import Client


FILESTACK_API_KEY = 'Abnq7E6rVRaiHd14Jibe8z'
SCREENSHOTLAYER_API_KEY = 'dd6ed8cb773d1335eb9c04fc8eaa4705'
SCREENSHOTLAYER_API_URL = 'http://api.screenshotlayer.com/api/capture'


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
        'access_key': SCREENSHOTLAYER_API_KEY,
        'url': url,
        'viewport': '1440x900',
        'width': '250'
    }

    response = requests.get(SCREENSHOTLAYER_API_URL, params=payload)
    im = Image.open(BytesIO(response.content))
    box = (0, 23, *im.size)
    croped_im = im.crop(box)
    croped_im.save('thumbnail.png')


def get_website_thumbnail_url():
    client = Client(FILESTACK_API_KEY)
    file = client.upload(filepath='thumbnail.png')

    return file.url


def generate_website_thumbnail(url):
    create_website_thumbnail_image(url)
    return get_website_thumbnail_url()
