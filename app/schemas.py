from typing import List, Union

from pydantic import BaseModel


class BookmarkBase(BaseModel):
    title: Union[str, None] = None
    icon_url: Union[str, None] = None
    url: str


class BookmarkCreate(BookmarkBase):
    pass


class Bookmark(BookmarkBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    password2: str


class User(UserBase):
    id: int
    bookmarks: List[Bookmark] = []

    class Config:
        orm_mode = True
