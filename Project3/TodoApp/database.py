# Este arquivo configura a conexão e sessão do banco de dados SQLite usando o ORM SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define a URL de conexão para um banco SQLite local chamado todos.db no diretório atual.
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'

# create_engine: Cria a conexão com o banco de dados
# Cria o engine que gerencia a conexão. O parâmetro check_same_thread: False permite que o SQLite seja usado em threads diferentes (necessário para FastAPI).
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

# sessionmaker: Factory para criar sessões de banco de dados
# autocommit=False: Transações devem ser commitadas manualmente
# autoflush=False: Não faz flush automático das mudanças
# bind=engine: Vincula ao engine criado
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# declarative_base: Base para criar modelos ORM
# Classe base que será herdada pelos modelos ORM para mapear tabelas do banco de dados.
Base = declarative_base()
