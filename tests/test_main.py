import pytest
import requests


class MockResponse:
    text = """<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <!-- <link rel="icon" href="/favicon.ico"> -->
                <link
                href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:ital,wght@0,400;1,700&display=swap"
                rel="stylesheet">
                <link
                href="https://fonts.googleapis.com/icon?family=Material+Icons"
                rel="stylesheet">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Vite App</title>
            </head>
            <body>
                <div id="app"></div>
                <script type="module" src="/src/main.js"></script>
            </body>
            </html>
        """


@pytest.fixture
def mock_response(monkeypatch):
    def get_mock(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', get_mock)


def test_login(client):
    """ Should return token to the client """
    response = client.post(
        '/login',
        data={'username': 'test', 'password': 'test'}
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_login_fail(client):
    """ Should return error message if login failed """
    response = client.post(
        '/login',
        data={'username': 'username', 'password': 'password'}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == 'Incorrect username or password.'


def test_register(client):
    """ Should create new user in database """
    response = client.post(
        '/register',
        json={
            'username': 'new_username',
            'password': 'somepassword',
            'password2': 'somepassword'
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['registration_status'] == 'Success'


@pytest.mark.parametrize(
    'username, password, password2, message',
    ((
        ('test', 'test', 'test', 'User already exists.'),
        ('test2', 'password', 'notpassword', 'Passwords doesn\'t match.')
    )))
def test_register_fail(client, username, password, password2, message):
    """ Should return error message if register failed """
    response = client.post(
        '/register',
        json={
            'username': username,
            'password': password,
            'password2': password2
        }
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == message


def test_profile(client, auth):
    """ Should return current user profile """
    auth.login()
    response = client.get('/profile', headers=auth.authHeader)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['username'] == 'test'


@pytest.mark.add
def test_add_bookmark(client, auth, mock_response):
    """ Should add new bookmark to the user's bookmark list """
    bookmark = {'url': 'http://testurl.com', 'tags': 'tag1,tag2'}
    auth.login()
    response = client.post(
        '/bookmarks/add',
        json=bookmark,
        headers=auth.authHeader
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['title'] == 'Vite App'
    assert data['tags'] == 'tag1,tag2'


def test_get_bookmarks(client, auth):
    """ Should return list of user bookmarks """
    auth.login()
    response = client.get('/bookmarks', headers=auth.authHeader)

    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_update_bookmarks(client, auth):
    """ Should update bookmark in database and return it """
    auth.login()
    response = client.get('/bookmarks', headers=auth.authHeader)
    bookmarks = response.json()

    bookmark_to_update = bookmarks[1]
    bookmark_to_update['title'] = 'Updated title'
    response = client.put(
        '/bookmarks',
        json=bookmark_to_update,
        headers=auth.authHeader
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['title'] == bookmark_to_update['title']


def test_delete_bookmarks(client, auth):
    """ Should delete bookmark from database and return message """
    auth.login()
    response = client.get('/bookmarks', headers=auth.authHeader)
    bookmarks = response.json()

    bookmark = bookmarks[1]
    response = client.delete(
        f'/bookmarks/{bookmark["id"]}',
        headers=auth.authHeader
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['deletion_status'] == 'Success'
