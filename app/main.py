from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import timedelta
from .utils import (
    get_website_title,
    is_valid_url,
    get_website_icon_url,
    generate_website_thumbnail
)
from . import crud, schemas
from .models import Base, User
from .security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    oauth2_scheme,
    create_access_token,
    verify_password
)
from .database import get_db, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def authenticate_user(db: Session, username: str, password: str):
    db_user = crud.get_user_by_username(db=db, username=username)
    if not db_user:
        return False
    if not verify_password(password, db_user.hashed_password):
        return False
    return db_user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db=db, username=username)
    if user is None:
        raise credentials_exception
    return user


@app.post('/login')
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    # print(user)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Incorrect username or password.',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token_exipres = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_exipres
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/register')
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db=db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail='User already exists.')
    crud.create_user(db=db, user=user)
    if user.password != user.password2:
        raise HTTPException(status_code=400, detail='Passwords doesn\'t match.')
    return {'registration_status': 'Success'}


@app.get("/profile")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get('/bookmarks')
async def get_bookmarks(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    return current_user.bookmarks


@app.post('/bookmarks/add')
async def add_bookmark(
        link: schemas.Link,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if is_valid_url(link.url) is False:
        raise HTTPException(status_code=400, detail='Url must begin with "http(s)://".')
    bookmark = schemas.BookmarkCreate(**link.dict())
    bookmark.title = get_website_title(bookmark.url)
    bookmark.icon_url = get_website_icon_url(bookmark.url)
    bookmark.thumbnail = generate_website_thumbnail(bookmark.url)
    return crud.create_bookmark(db, bookmark, current_user.id)


@app.put('/bookmarks')
async def update_bookmark(
        bookmark: schemas.Bookmark,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    if current_user.id != bookmark.owner_id:
        raise HTTPException(status_code=400, detail='Bookmark does\'t exist')
    return crud.update_bookmark(db, bookmark)


@app.delete('/bookmarks/{bookmark_id}')
async def delete_bookmark(
        bookmark_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)):
    bookmark = crud.get_bookmark_by_id(db, bookmark_id)
    if not bookmark:
        raise HTTPException(status_code=400, detail='Bookmark does\'t exist')
    if current_user.id != bookmark.owner_id:
        raise HTTPException(status_code=400, detail='Bookmark does\'t exist')
    crud.delete_bookmark(db, bookmark_id)
    return {'deletion_status': 'Success'}
