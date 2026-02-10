# Importações principais usadas nos testes:
# - sqlalchemy: para conectar/criar uma sessão de teste com o banco
# - FastAPI TestClient: para fazer requisições ao app durante os testes
# - pytest: para fixtures e execução dos testes
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..database import Base
from ..main import app
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

# URL do banco de dados usado nos testes.
# Aqui está apontando para um Postgres local "TodoTestDatabase".
# Observação: em muitos setups de CI/tests locais prefere-se usar SQLite em memória, enquanto o DB principal é com POSTGREs
SQLALCHEMY_DATABASE_URL = 'sqlite:///./testdb.db'

# Criação do engine de SQLAlchemy.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

# Fábrica de sessões usada apenas nos testes (TestingSessionLocal).
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Garante que as tabelas declaradas (Base.metadata) existam no banco de teste.
# Isso cria as tabelas necessárias antes de executar os testes.
Base.metadata.create_all(bind=engine)

# Função que substitui (override) a dependência get_db do FastAPI para usar a sessão de teste.
# FastAPI permite sobrescrever dependências durante testes para injetar uma sessão de teste.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função que substitui (override) a dependência get_current_user para simular um usuário autenticado.
# Aqui retornamos um dicionário simples com username, id e role.
# Isso evita a necessidade de autenticar via tokens durante os testes.
def override_get_current_user():
    return {'username': 'lucasb', 'id': 1, 'user_role': 'admin'}

# Cliente de teste que faz requisições HTTP ao app FastAPI.
client = TestClient(app)

# Uma fixture no pytest é uma função que prepara dados ou recursos necessários para os testes executarem.
# Ela funciona como um provedor de dependências que configura o ambiente antes dos testes.
# Principais características das fixtures:
# 1. Preparação de dados - Criam objetos, conexões de banco, arquivos temporários
# 2. Reutilização - Podem ser usadas por múltiplos testes
# 3. Injeção de dependência -O pytest automaticamente "injeta" a fixture nos testes que a requisitam
# 4. Limpeza automática (com yield)
# Código antes do yield: executa antes do teste (setup)
# Código após o yield: executa após o teste (teardown)

# Fixture pytest que cria um To do no banco antes do teste e garante limpeza após o teste.
# A fixture devolve o objeto to do para que os testes possam usá-lo diretamente.
# Sem fixtures, você teria que repetir o código de criação e limpeza em cada teste. Com fixtures, o pytest gerencia isso automaticamente.
@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )

    # Abre uma sessão de teste, adiciona o objeto e faz commit para persistir no DB de teste.
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    # Entrega o to do para o teste que depender desta fixture.
    # Sem o yield, a fixture seria apenas uma função normal que executa tudo de uma vez.
    # Com o yield, se torna um gerenciador de contexto que garante limpeza automática após cada teste,
    # dividindo oc código em antes e depois dos testes
    yield todo

    # Limpeza: após o teste, removemos todos os registros da tabela todos.
    # Usamos conexão direta e comando SQL para garantir remoção.
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    # Cria uma instância do modelo Users com dados de teste fixos
    # Isso garante que todos os testes que usam esta fixture tenham os mesmos dados de usuário
    user = Users(
        username="lucasb",
        email="lucasb@email.com",
        first_name="Lucas",
        last_name="Balbueno",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )
    db = TestingSessionLocal()
    
    # Adiciona o usuário à sessão (staging area)
    # Neste ponto o usuário ainda não foi salvo no banco
    db.add(user)
    
    # Executa o commit para persistir o usuário no banco de dados de teste
    # Agora o usuário está efetivamente salvo e pode ser consultado pelos testes
    db.commit()
    
    # Yield pausa a execução e "entrega" o objeto user para o teste
    # O teste recebe este objeto e pode usá-lo diretamente
    # Após o teste terminar, a execução continua na linha seguinte
    yield user
    
    # LIMPEZA (teardown): Executa após cada teste que usa esta fixture
    # Abre uma conexão direta com o banco para executar SQL bruto
    with engine.connect() as connection:
        # Remove TODOS os registros da tabela users para garantir isolamento entre testes
        # Usamos SQL direto (text()) para garantir que a limpeza seja efetiva
        connection.execute(text("DELETE FROM users;"))
        # Confirma a operação de limpeza no banco
        connection.commit()