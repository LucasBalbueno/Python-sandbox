from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from models import Users
from database import SessionLocal
from .auth import get_current_user
from passlib.context import CryptContext

# Instancia de uma rota para ser usado na main
router = APIRouter(
    prefix='/users',
    tags=['users']
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
# Ao botar essa dependencia como parametro da rota, ele automaticamente exige que a rota seja autenticada
user_dependency = Annotated[dict, Depends(get_current_user)]

# Criando contexto para criptografar a senha
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserPasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=3)

@router.get('/user', status_code=status.HTTP_200_OK)
async def get_current_user (user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    return db.query(Users).filter(Users.id == user.get('id')).first() # type: ignore

@router.put('/user/update_password', status_code=status.HTTP_200_OK)
async def update_password (user: user_dependency, db: db_dependency, user_password_request: UserPasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first() # type: ignore

    if not bcrypt_context.verify(user_password_request.password, user_password_request.new_password):
        raise HTTPException(status_code=401, detail='Error on password change')

    user_model.hashed_password = bcrypt_context.hash(user_password_request.new_password)

    db.add(user_model)
    db.commit()