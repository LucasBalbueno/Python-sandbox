# Este código define um modelo SQLAlchemy para uma tabela de tarefas (todos).

# Base: Classe base importada do arquivo database.py que contém a configuração do SQLAlchemy
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# Criando tabela users
class Users(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    phone_number = Column(String)

# Criando tabela todos
class Todos(Base):
    __tablename__= 'todos'

    # Campo ID como chave primária inteira com índice para melhor performance
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    # Configurando a ForeignKey id de users
    owner_id = Column(Integer, ForeignKey("users.id"))