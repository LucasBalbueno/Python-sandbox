# uvicorn main:app --reload (na pasta TodoApp)

from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos

# Instancia a aplicação FastAPI.
app = FastAPI()

# Cria todas as tabelas definidas nos modelos no banco de dados usando o engine configurado.
# Essa opção faz com o que o banco seja criado ao executar a main
models.Base.metadata.create_all(bind=engine)

# Incluindo todos os métodos auth de auth.py na main
app.include_router(auth.router)

# Incluindo todos os métodos de to do de todos.py na main
app.include_router(todos.router)