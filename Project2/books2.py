# uvicorn Project2.books2:app --reload (for run this code)
# fastapi run Project2.books2.py (for run production mode)
# fastapi dev Project2.books2.py (for run development mode)

from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
# Pydantic é usado para análise de dados e validação de dados
from pydantic import BaseModel, Field
# Usado para validações HTTP (informar o status Code)
from starlette import status

# Cria a aplicação FastAPI
app = FastAPI()

# Classe simples em Python que representa um livro (não é um modelo Pydantic)
class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    # Inicializando o construtor com os atributos do objeto Book
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

# Modelo Pydantic usado para validar o corpo da requisição
# Field é usado para criar validações em campos específicos
class BookRequest(BaseModel):
    id: Optional[int] = Field(description='O ID não é necessário', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6) #Maior que 0 e menor que 6
    published_date: int = Field(gt=1999, lt=2031)

    # Configurações de models da requisição pydantic
    model_config = {
        "json_schema_extra": {
            "example": {
            "title": "A new book",
            "author": "Lucas Balbueno",
            "description": "A new description",
            "rating": 5,
            "published_date": "2025"
            }
        }
    }


# Lista em memória que guarda instâncias de livros
# Esta lista é temporária: existe apenas enquanto a aplicação rodar
BOOKS = [
    Book(1, 'Compute Science Pro', 'Lucas Balbueno', 'A very nice book!', 5, 2025),
    Book(2, 'Fast API', 'Lucas Balbueno', 'A very nice book 2!', 5, 2021),
    Book(3, 'Endpoints', 'Lucas Balbueno', 'A very nice book 3!', 5, 2001),
    Book(4, 'HP1', 'Author 1', 'A very nice book 4!', 1, 2003),
    Book(5, 'HP2', 'Author 2', 'A very nice book 5!', 2, 2015),
    Book(6, 'HP3', 'Author 3', 'A very nice book 6!', 3, 2029)
]

# GET Method
@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

# Pegando livro pelo id (Path parameter)
@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    # Lançando um HTTPException
    raise HTTPException(status_code=404, detail='Item not found')

# Pegando livro pelo rating (Query parameter)
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_published_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

# POST Method with Body parameter
@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    # model_dump() transforma uma instancia de BaseModel (Pydantic) para uma estrutura python (dictionary, object...)
    # Recebe pydantic como argumento para poder validar > transforma em estrutura python (new_book)
    # ** → converte dicionário em argumentos nomeados
    new_book = Book(**book_request.model_dump())

    # Adiciona o novo livro ao final da lista BOOKS
    BOOKS.append(find_book_id(new_book))

# Função para achar o último ID em BOOKS
def find_book_id(book: Book):
    # Se for mais que 0 então pegará o ID do último book e somar mais 1
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1

    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')