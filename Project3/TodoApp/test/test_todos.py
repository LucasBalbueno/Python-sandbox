# Importações principais usadas nos testes:
# - get_db e get_current_user para aplicar os overrides criados
# - fastapi status para indicar os status HTTP em cada teste
from ..routers.todos import get_db, get_current_user
from fastapi import status
from .utils import *

# Aplica as sobrescritas de dependência ao app FastAPI para toda a execução dos testes.
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Teste que verifica leitura de todos os To do.
def test_read_all_authenticated(test_todo):
    response = client.get("/")
    # O assert verifica status HTTP 200 OK.
    assert response.status_code == status.HTTP_200_OK
    # A comparação JSON abaixo precisa corresponder exatamente ao que a rota retorna.
    assert response.json() == [{'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}]

# Teste que verifica a leitura de um único to do específico.
def test_read_one_authenticated(test_todo):
    # Faz uma requisição GET para buscar o to do com id=1 criado pela fixture.
    response = client.get("/todo/1")
    # Verifica se a resposta retorna status HTTP 200 (OK), indicando sucesso.
    assert response.status_code == status.HTTP_200_OK
    # Valida se o JSON retornado corresponde exatamente aos dados do to do criado pela fixture.
    assert response.json() == {'complete': False, 'title': 'Learn to code!',
                                'description': 'Need to learn everyday!', 'id': 1,
                                'priority': 5, 'owner_id': 1}

# Teste que verifica o comportamento quando tenta buscar um to do que não existe.
def test_read_one_authenticated_not_found():
    # Faz requisição GET para um to do com id=999 que não existe no banco.
    response = client.get("/todo/999")
    # Verifica se retorna status HTTP 404 (Not Found), indicando que o recurso não foi encontrado.
    assert response.status_code == status.HTTP_404_NOT_FOUND
    # Valida se a mensagem de erro retornada está correta e padronizada.
    assert response.json() == {'detail': 'Todo not found.'}

# Teste que verifica a criação de um novo to do via POST.
# Utiliza a fixture test_todo para garantir que já existe pelo menos um to do no banco (id=1).
# Assim, o novo to do criado terá id=2.
def test_create_todo(test_todo):
    # Dados do novo to do a ser criado via requisição POST.
    request_data={
        'title': 'New Todo!',
        'description':'New todo description',
        'priority': 5,
        'complete': False,
    }

    # Faz requisição POST para criar o novo to do, enviando os dados como JSON.
    response = client.post('/todos/', json=request_data)
    # Verifica se retorna status HTTP 201 (Created), indicando que o recurso foi criado com sucesso.
    assert response.status_code == 201

    # Validação adicional: consulta diretamente o banco para confirmar que o to do foi persistido.
    # Abre uma nova sessão de banco para buscar o to do recém-criado (deve ter id=2).
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first() # type: ignore

    # Verifica se cada campo foi salvo corretamente no banco, comparando com os dados enviados.
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

# Teste que verifica a atualização de um to do existente via PUT.
# Usa a fixture test_todo que cria um to do com id=1 antes do teste para ser atualizado.
def test_update_todo(test_todo):
    # Dados para atualizar o to do existente. Mudamos principalmente o título para verificar a atualização.
    request_data={
        'title':'Change the title of the todo already saved!',  # Novo título para verificar a mudança
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    # Faz requisição PUT para atualizar o to do com id=1, enviando os novos dados como JSON.
    response = client.put('/todos/1', json=request_data)
    # Verifica se retorna status HTTP 204 (No Content), indicando atualização bem-sucedida sem retorno de dados.
    assert response.status_code == 204

    # Validação adicional: consulta o banco diretamente para confirmar que a atualização foi persistida.
    # Abre uma nova sessão e busca o to do atualizado pelo id=1.
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first() # type: ignore
    # Verifica se o título foi realmente alterado para o novo valor enviado na requisição.
    assert model.title == 'Change the title of the todo already saved!'

# Teste que verifica o comportamento ao tentar atualizar um to do que não existe.
def test_update_todo_not_found(test_todo):
    # Dados válidos para atualização, mas serão enviados para um to do que não existe.
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    # Tenta fazer PUT para o to do com id=999 que não existe no banco.
    response = client.put('/todos/999', json=request_data)
    # Verifica se retorna status HTTP 404 (Not Found), indicando que o to do não foi encontrado.
    assert response.status_code == 404
    # Confirma que a mensagem de erro está correta e padronizada.
    assert response.json() == {'detail': 'Todo not found.'}


# Teste que verifica a exclusão de um to do existente via DELETE.
# Utiliza a fixture test_todo que cria um to do com id=1 para ser deletado durante o teste.
def test_delete_todo(test_todo):
    # Faz requisição DELETE para remover o to do com id=1 criado pela fixture.
    response = client.delete('/todo/1')
    # Verifica se retorna status HTTP 204 (No Content), indicando exclusão bem-sucedida.
    assert response.status_code == 204

    # Validação adicional: confirma que o to do foi realmente removido do banco de dados.
    # Abre uma nova sessão de banco para verificar se o registro ainda existe.
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first() # type: ignore
    # Se a exclusão funcionou corretamente, a consulta deve retornar None.
    assert model is None


# Teste que verifica o comportamento ao tentar deletar um to do que não existe.
def test_delete_todo_not_found():
    # Faz requisição DELETE para um to do com id=999 que não existe no banco.
    response = client.delete('/todo/999')
    # Verifica se retorna status HTTP 404 (Not Found), indicando que o to do a ser deletado não foi encontrado.
    assert response.status_code == 404
    # Confirma que a mensagem de erro retornada está correta e informativa.
    assert response.json() == {'detail': 'Todo not found.'}