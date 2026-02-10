from .utils import *
# Importa as funções principais do módulo de autenticação que serão testadas:
# - get_db: função que cria sessões do banco de dados
# - authenticate_user: valida credenciais de login (username/password)
# - create_access_token: gera tokens JWT para sessões autenticadas
# - SECRET_KEY: chave secreta para assinar/validar tokens JWT
# - ALGORITHM: algoritmo usado para criptografar tokens (geralmente HS256)
# - get_current_user: extrai e valida informações do usuário a partir do token JWT
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
# Biblioteca para trabalhar com tokens JWT (JSON Web Tokens)
# jwt.decode: decodifica e valida tokens
# jwt.encode: cria novos tokens
from jose import jwt
# Para trabalhar com intervalos de tempo nos tokens (tempo de expiração)
from datetime import timedelta
import pytest
from fastapi import HTTPException

app.dependency_overrides[get_db] = override_get_db

# Testa a função authenticate_user que verifica credenciais de login.
# A função authenticate_user:
# 1. Busca o usuário pelo username no banco
# 2. Verifica se a senha fornecida confere com a senha hasheada armazenada
# 3. Retorna o objeto User se autenticado, False se falhar
def test_authenticate_user(test_user):
    # Cria uma sessão do banco de teste para passar para a função authenticate_user
    db = TestingSessionLocal()

    # Deve retornar o objeto User completo quando username e password estão corretos
    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    # Verifica que o usuário foi autenticado com sucesso (não retornou None/False)
    assert authenticated_user is not None
    # Verifica que o username do usuário retornado confere com o esperado
    assert authenticated_user.username == test_user.username

    # Deve retornar False quando o usuário não existe no banco
    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    # Username correto, mas senha errada - deve retornar False
    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False

# Testa a função create_access_token que gera tokens JWT para sessões autenticadas.
# Um token JWT contém:
# - sub (subject): identificação do usuário (username)
# - id: ID numérico do usuário no banco
# - role: papel/permissão do usuário (admin, user, etc.)
# - exp (expiration): timestamp de quando o token expira
def test_create_access_token():
    # Define dados de teste para criar o token
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    # Chama a função que cria o token JWT com os dados fornecidos
    token = create_access_token(username, user_id, role, expires_delta)

    # Decodifica o token para verificar se os dados foram incluídos corretamente
    # options={'verify_signature': False}: pula verificação da assinatura para simplificar o teste. Em produção, a assinatura sempre deve ser verificada para garantir integridade
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                               options={'verify_signature': False})

    # Verifica se cada campo foi incluído corretamente no payload do token
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


# @pytest.mark.asyncio informa ao pytest que esta é uma função assíncrona
# Por padrão, pytest não sabe como executar funções async - precisa desta marcação
# Testa a função get_current_user com um token JWT válido e completo.
# A função get_current_user:
# 1. Decodifica o token JWT usando a SECRET_KEY
# 2. Extrai username, id e role do payload
# 3. Retorna um dicionário com as informações do usuário
# 4. Lança HTTPException se o token for inválido ou incompleto
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Cria manualmente um payload com todos os campos necessários
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}

    # Gera um token JWT válido usando o payload e a chave secreta do sistema
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # Chama a função que extrai informações do usuário a partir do token
    # Esta função é assíncrona, então precisa do 'await'
    user = await get_current_user(token=token)

    # Verifica se a função retorna exatamente o dicionário esperado
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}


# Testa a função get_current_user com um token que tem payload incompleto.
# Quando campos obrigatórios estão ausentes, a função deve:
# 1. Detectar que o payload está incompleto
# 2. Lançar HTTPException com status 401 (Unauthorized)
# 3. Incluir mensagem de erro específica
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    # Cria um payload inválido que não tem os campos obrigatórios 'sub' e 'id'
    encode = {'role': 'user'}

    # Gera um token com o payload incompleto
    # O token será válido em termos de estrutura/assinatura, mas com dados insuficientes
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # pytest.raises() verifica se uma exceção específica é lançada
    # 'with' captura a exceção para que possamos inspecionar seus detalhes
    with pytest.raises(HTTPException) as excinfo:
        # Tenta usar o token inválido - deve lançar HTTPException
        await get_current_user(token=token)

    # Verifica se a exceção tem o código de status correto (401 Unauthorized)
    assert excinfo.value.status_code == 401

    # Verifica se a mensagem de erro é exatamente a esperada
    assert excinfo.value.detail == 'Could not validate user.'