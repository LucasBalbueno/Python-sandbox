# Arquivos com rotas to do

from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from models import Todos
from database import SessionLocal
from .auth import get_current_user

# Instancia de uma rota para ser usado na main
router = APIRouter()

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

# Criando uma dependência para pegar o username, role e id do usuário autenticado
# Ao botar essa dependencia como parametro da rota, ele automaticamente exige que a rota seja autenticada
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

# Endpoint para pegar tudo de Todos
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db:db_dependency):
    # user_dependency pega as informações do usuário autenticado e diz que a rota deve ter autenticação
    # Se user é vazio, retorna um erro, pois quer dizer que não tem usuário autenticado
    if user is None:
        raise HTTPException(status_code=301, detail='Authentication Failed')

    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all() # type: ignore

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # user_dependency pega as informações do usuário autenticado e diz que a rota deve ter autenticação
    # Se user é vazio, retorna um erro, pois quer dizer que não tem usuário autenticado
    if user is None:
        raise HTTPException(status_code=301, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first() # type: ignore
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')

@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    # user_dependency pega as informações do usuário autenticado e diz que a rota deve ter autenticação
    # Se user é vazio, retorna um erro, pois quer dizer que não tem usuário autenticado
    if user is None:
        raise HTTPException(status_code=301, detail='Authentication Failed')

    # todo_request.model_dump(): Converte o objeto Pydantic em um dicionário
    # ** todo_request.model_dump(): Desempacota o dicionário como argumentos nomeados
    # Todos(...): Cria uma instância do modelo SQLAlchemy com os dados recebidos
    # Temos que passa também o owner_id dentro da requisição, para atribuir o to do ao usuário autenticado
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    # Adiciona o novo to do a sessão(ainda não salva no banco)
    db.add(todo_model)
    # Confirma a transação e salva definitivamente no banco de dados
    db.commit()

@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    # user_dependency pega as informações do usuário autenticado e diz que a rota deve ter autenticação
    # Se user é vazio, retorna um erro, pois quer dizer que não tem usuário autenticado
    if user is None:
        raise HTTPException(status_code=301, detail='Authentication Failed')

    # Filtra pelo id do to do e pelo id do usuário
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first() # type: ignore

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # user_dependency pega as informações do usuário autenticado e diz que a rota deve ter autenticação
    # Se user é vazio, retorna um erro, pois quer dizer que não tem usuário autenticado
    if user is None:
        raise HTTPException(status_code=301, detail='Authentication Failed')

    # Filtra pelo id do to do e pelo id do usuário
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first() # type: ignore

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete() # type: ignore
    db.commit()