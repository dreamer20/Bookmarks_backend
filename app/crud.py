from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_bookmark(db: Session, bookmark: schemas.BookmarkCreate, user_id: int):
    db_bookmark = models.Bookmark(**bookmark.dict(), owner_id=user_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


def update_bookmark(db: Session, bookmark: schemas.Bookmark):
    db.query(models.Bookmark).filter(models.Bookmark.id == bookmark.id).update(bookmark.dict())
    db.commit()
    return db.query(models.Bookmark).filter(models.Bookmark.id == bookmark.id).first()


def delete_bookmark(db: Session, id: int):
    db.query(models.Bookmark).filter(models.Bookmark.id == id).delete()
    db.commit()


def get_bookmark_by_id(db: Session, id: int):
    return db.query(models.Bookmark).filter(models.Bookmark.id == id).first()


def get_user_bookmarks(db: Session, user_id: int):
    return db.query(models.Bookmark).filter(models.Bookmark.owner_id == user_id).all()
