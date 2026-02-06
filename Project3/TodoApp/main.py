# uvicorn main:app --reload (na pasta TodoApp)

from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users

# Instancia a aplicação FastAPI.
app = FastAPI()

# Cria todas as tabelas definidas nos modelos no banco de dados usando o engine configurado.
# Essa opção faz com o que o banco seja criado ao executar a main
Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}

# Incluindo todos os métodos HTTP auth de auth.py na main
app.include_router(auth.router)

# Incluindo todos os métodos HTTP de to do de todos.py na main
app.include_router(todos.router)

# Incluindo todos os métodos HTTP admin de admin.py na main
app.include_router(admin.router)

# Incluindo todos os métodos HTTP users de users.py na main
app.include_router(users.router)