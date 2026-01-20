# uvicorn Project1.books:app --reload (for run this code)
# fastapi run Project1.books.py (for run production mode)
# fastapi dev Project1.books.py (for run development mode)

# import fastapi lib
from fastapi import FastAPI, Body

# This allow Uvicorn to identify a new fastapi application
# Uvicorn is the web server we use to start a FastAPI application
app = FastAPI()

# Books information
BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

#"/docs" in browser for open Swagger documentation
#HTTP GET METHOD (READ)
@app.get("/books")
async def get_all_books():
    return BOOKS

#HTTP get request with Path Parameter
#Requests with Path Parameters should be below Requests with fixed params.
@app.get("/books/{book_title}")
# Setting the path param for str
async def get_book_by_title(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
    return None


#HTTP get request with Query Parameter
@app.get("/books/")
async def get_books_by_category(category: str):
    books_category = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            books_category.append(book)
    return books_category

#HTTP get request with Path and Query Parameters
@app.get("/books/{author}/")
async def get_books_by_category_and_author(author: str, category: str):
    books_author_category = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold() and book.get('category').casefold() == category.casefold():
            books_author_category.append(book)
    return books_author_category

#HTTP POST METHOD (CREATE)
#HTTP post request with body param
@app.post("/books/create_book")
async def create_book(new_book = Body()):
    BOOKS.append(new_book)

#HTTP post request with TYPE body param
@app.post("/books/create_book")
# Setting the body param for dictionary
async def create_book(new_book: dict = Body()):
    BOOKS.append(new_book)

#HTTP PUT METHOD (UPDATE)
#HTTP put request with body param
@app.put("/books/update_book")
async def update_book(updated_book: dict = Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book

#HTTP DELETE METHOD (DELETE)
#HTTP delete request with path param
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break