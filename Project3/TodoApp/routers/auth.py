# Arquivos com rotas auth e lógica de JWT token
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

router = APIRouter()

# KEYS para usar no jwt token
SECRET_KEY = 'fcfb2b42cbc06959fd50cd70084e0bd92e5aca9383ddc675a4017eb587b5dee9'
ALGORITHM = 'HS256'

# Essa função pega o username, a senha e a dependência do banco de dados
# Verifica se o username existe no banco de dados, se não retorna False
# Verifica se a senha passada é a mesma senha criptografada salva no banco
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# O objetivo da função é criar um JWT com as claims sub (username), id (user id) e exp (expiração).
def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

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

# Configurando o bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Classe do tipo request para criar um usuário
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        hashed_password =bcrypt_context.hash(create_user_request.password),
        is_active = True
    )

    # Poderíamos criar desta forma, pois isso é como um desestruturador de dicionários.
    # Nesse caso específico não podemos porque o campo password e hashed_password possuem nomes diferentes
    # create_user_model = Users(**create_user_request.model_dump())

    db.add(create_user_model)
    db.commit()

# Method HTTP para criar um Token
# O OAuth2PasswordRequestForm é um formulário padrão do FastAPI para pedir o username, a senha, client_id e outras informações de credenciais do usuário
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    # Chamando a função que verifica se o username e senha no banco de dados existe e estão corretos
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return 'Failed Authentication'

    # Criando um token de acesso passando o username, id e o tempo de expiração
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    # Retornando o token JWT para o method criar token
    return {'access_token': token, 'token_type': 'bearer'}