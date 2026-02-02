from typing import Generator, Any

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud
from database import SessionLocal
from schemas import Author, AuthorCreate, Book, BookCreate, PaginatedResponse

app = FastAPI()


def get_db() -> Generator[Any, Any, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/authors/", response_model=PaginatedResponse[Author])
def get_authors(
        db: Session = Depends(get_db),
        page: int = 1,
        size: int = 10,
        name: str | None = Query(default=None, min_length=3, max_length=50),
):
    return crud.get_all_authors(db=db, page=page, size=size, name=name)


@app.get("/authors/{author_id}", response_model=Author)
def get_author_by_id(author_id: int, db: Session = Depends(get_db)):
    return crud.get_author_by_id(db, author_id)


@app.post("/authors/", response_model=Author)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = crud.get_author_by_name(db, author.name)
    if db_author:
        raise HTTPException(status_code=400, detail="Author already exists")
    return crud.create_author(db, author)


@app.get("/books/", response_model=PaginatedResponse[Book])
def get_books(
        db: Session = Depends(get_db),
        page: int = 1,
        size: int = 10,
        title: str | None = Query(default=None, min_length=3, max_length=50),
        author_id: int | None = Query(default=None),
):
    return crud.get_all_books(db=db, page=page, size=size, title=title, author_id=author_id)


@app.get("/books/{book_id}/", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return crud.get_book_by_id(db, book_id)


@app.post("/books/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = crud.get_book_by_title_and_author(db, book.title, book.author_id)
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists")
    return crud.create_book(db, book)
