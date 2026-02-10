from .utils import *
# Importa as dependências originais do router admin que serão substituídas nos testes
from ..routers.admin import get_db, get_current_user
# Importa códigos de status HTTP para verificações nos testes
from fastapi import status
# Importa o modelo Todos para consultas diretas ao banco durante os testes
from ..models import Todos

# Aplica as sobrescritas de dependência ao app FastAPI para toda a execução dos testes.
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Testa o endpoint GET /admin/to-do para listar todos os todos (apenas para admins)
# test_todo: Fixture que cria um to do no banco antes do teste
def test_admin_read_all_authenticated(test_todo):
    # Faz requisição GET para o endpoint de admin que lista todos os todos
    response = client.get("/admin/todo")
    # Verifica se a resposta retornou status 200 (OK)
    assert response.status_code == status.HTTP_200_OK
    # Verifica se o JSON retornado contém exatamente o to do criado pela fixture
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]

# Testa o endpoint DELETE /admin/to-do/{todo_id} para excluir um to do específico
def test_admin_delete_todo(test_todo):
    # Faz requisição DELETE para excluir o to do com ID 1
    response = client.delete("/admin/todo/1")
    # Verifica se a resposta retornou status 204 (No Content)
    # Código 204 indica que a operação foi bem-sucedida mas não há conteúdo para retornar
    assert response.status_code == 204
    # Cria uma nova sessão de banco para fazer a consulta
    db = TestingSessionLocal()
    # Verifica se o to do foi realmente excluído do banco de dados
    model = db.query(Todos).filter(Todos.id == 1).first()

    # Verifica se a consulta retornou None, confirmando que o to do foi excluído
    assert model is None

# Testa o comportamento do endpoint DELETE quando tenta excluir um to do inexistente
# Este teste verifica o tratamento de erro quando o ID não existe no banco
def test_admin_delete_todo_not_found():
    # Faz requisição DELETE para um ID que não existe (999)
    response = client.delete("/admin/todo/999")
    # Verifica se retornou status 404 (Not Found)
    assert response.status_code == 404
    # Verifica se a mensagem de erro está correta
    assert response.json() == {'detail': 'Todo not found.'}