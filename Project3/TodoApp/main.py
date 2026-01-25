# uvicorn main:app --reload (na pasta TodoApp)

from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, Path, HTTPException
from starlette import status

import models
from models import Todos
from database import engine, SessionLocal

# Instancia a aplicação FastAPI.
app = FastAPI()

# Cria todas as tabelas definidas nos modelos no banco de dados usando o engine configurado.
models.Base.metadata.create_all(bind=engine)

# Cria sessão do banco
def get_db():
    db = SessionLocal()
    try:
        # Yield serve para criar generators, ela pausa a função e retorna a execução após o valor ter sido retornado.
        # O yield garante que a sessão do banco seja sempre fechada, mesmo se houver erros no endpoint. Diferentemente se tivéssemos usado o return.
        yield db
    # finally: Garante que a sessão seja fechada após o uso
    finally:
        db.close()

# Cria uma dependência reutilizável que: Anota o tipo como Session e usa Depends(get_db) para injetar a sessão do banco automaticamente
db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

# Endpoint para pegar tudo de Todos
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db:db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first() # type: ignore
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    # todo_request.model_dump(): Converte o objeto Pydantic em um dicionário

    # ** todo_request.model_dump(): Desempacota o dicionário como argumentos nomeados

    # Todos(...): Cria uma instância do modelo SQLAlchemy com os dados recebidos
    todo_model = Todos(**todo_request.model_dump())

    # Adiciona o novo to do a sessão(ainda não salva no banco)
    db.add(todo_model)
    # Confirma a transação e salva definitivamente no banco de dados
    db.commit()

@app.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first() # type: ignore

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first() # type: ignore

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.query(Todos).filter(Todos.id == todo_id).delete() # type: ignore
    db.commit()