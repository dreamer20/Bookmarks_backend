import pytest
from app.utils import (
    get_website_title,
    get_website_icon_url,
    is_valid_url
)


def test_get_website_title():
    """ Should return website title """
    title = get_website_title('https://git-scm.com/')

    assert title == 'Git'


def test_get_website_title_fails():
    """ Should return default title if to get title is impossible """
    title = get_website_title('https://somenonexistenturl.com')

    assert title == 'Bookmark Title'


@pytest.mark.parametrize('url, expected', (
    ('https://git-scm.com/', 'https://git-scm.com/favicon.ico'),
    ('https://docs.python.org/3/tutorial/errors.html', 'https://docs.python.org/favicon.ico'),
    ('https://translate.google.com/?sl=en&tl=ru&text=nonexistent&op=translate', 'https://translate.google.com/favicon.ico'),
    ('https://translate', 'https://translate/favicon.ico')
))
def test_get_website_icon_url(url, expected):
    """ Should return website icon url """
    icon_url = get_website_icon_url(url)

    assert icon_url == expected


def test_is_valid_url():
    """ Should check if url is valid """
    assert is_valid_url('http://example.com') is True
    assert is_valid_url('http://example') is True
    assert is_valid_url('https://example.is') is True
    assert is_valid_url('example') is False
    assert is_valid_url('') is False
