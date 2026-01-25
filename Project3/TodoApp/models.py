# Este código define um modelo SQLAlchemy para uma tabela de tarefas (todos).

from database import Base
from sqlalchemy import Column, Integer, String, Boolean

# Base: Classe base importada do arquivo database.py que contém a configuração do SQLAlchemy
class Todos(Base):
    __tablename__= 'todos'

    # Campo ID como chave primária inteira com índice para melhor performance
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)