from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from ..models import Todos
from ..database import SessionLocal
from .auth import get_current_user

# Instancia de uma rota para ser usado na main
router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

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
# Ao botar essa dependência como parametro da rota, ele automaticamente exige que a rota seja autenticada
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    # Verifica se o usuário autenticado possui role admin
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Coleta todos os to do
    return db.query(Todos).all()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo (user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    # Verifica se o usuário autenticado possui role admin
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Verifica se o to do existe
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first() # type: ignore
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    # Exclui o to do específico pelo seu id
    db.query(Todos).filter(Todos.id == todo_id).delete() # type: ignore
    db.commit()