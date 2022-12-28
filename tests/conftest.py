from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.database import Base, get_db
from app.crud import create_user, create_bookmark
from app.main import app
from app.schemas import UserCreate, BookmarkCreate

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:peri54ri7end@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = TestingSessionLocal()
test_user = create_user(db, UserCreate(username='test', password='test', password2='test'))
create_bookmark(db, BookmarkCreate(title='Some title 1', url='http://someurl.com'), test_user.id)
create_bookmark(db, BookmarkCreate(title='Some title 2', url='http://someurl.com'), test_user.id)
create_bookmark(db, BookmarkCreate(title='Some title 3', url='http://someurl.com'), test_user.id)
db.close


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


class AuthUser:
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        response = self._client.post(
            '/login',
            data={'username': username, 'password': password}
        )
        data = response.json()
        self.token = data['access_token']
        self.authHeader = {'Authorization': f'Bearer {self.token}'}


@pytest.fixture
def auth(client):
    return AuthUser(client)
