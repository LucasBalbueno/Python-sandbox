# Arquivos com rotas auth e lógica de JWT token

from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# Configura as rotas para sempre começar com /auth
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# Configurando o bcrypt
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauh2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# KEYS para usar no jwt token
SECRET_KEY = 'fcfb2b42cbc06959fd50cd70084e0bd92e5aca9383ddc675a4017eb587b5dee9'
ALGORITHM = 'HS256'

# Essa função pega o username, a senha e a dependência do banco de dados
def authenticate_user(username: str, password: str, db):
    # Verifica se o username existe no banco de dados, se não retorna False
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    # Verifica se a senha passada é a mesma senha criptografada salva no banco
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: Annotated[str, Depends(oauh2_bearer)]):
    try:
        # decodifica e verifica o token usando SECRET_KEY e ALGORITHM.Se a assinatura / expiração falhar, JWTError é levantada
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # extrai as claims esperadas: subject(username) e user id
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        # Se qualquer claim estiver ausente, a função levanta HTTPException
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        return {'username': username, 'id': user_id}

    # Bloco de erro, captura os erros e devolver o erro 401
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

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

# Classe do tipo request para criar um usuário
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

# Classe do tipo request para criar um token
class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/", status_code=status.HTTP_201_CREATED)
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
    # Se não passar retorna um erro
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

    # Criando um token de acesso passando o username, id e o tempo de expiração
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    # Retornando o token JWT para o method criar token
    return {'access_token': token, 'token_type': 'bearer'}