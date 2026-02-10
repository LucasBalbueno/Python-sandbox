from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

# Aplica as sobrescritas de dependência ao app FastAPI para toda a execução dos testes.
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# Testa o endpoint GET /users/user que retorna informações do usuário autenticado.
# Fluxo do teste:
# 1. A fixture test_user cria um usuário no banco de teste
# 2. As dependências override garantem que:
#     - get_db retorna a sessão do banco de teste
#     - get_current_user retorna {'username': 'lucasb', 'id': 1, 'user_role': 'admin'}
# 3. O endpoint consulta o banco usando o ID do usuário mock (id=1)
# 4. Retorna os dados do usuário encontrado
def test_return_user(test_user):
    # Faz uma requisição GET para o endpoint que retorna dados do usuário atual
    response = client.get("/users/user")
    # Verifica se a resposta tem status 200 OK (sucesso)
    assert response.status_code == status.HTTP_200_OK

    # Converte a resposta para JSON e verifica cada campo retornado
    # Estes valores devem coincidir exatamente com os dados criados pela fixture test_user
    assert response.json()['username'] == 'lucasb'
    assert response.json()['email'] == 'lucasb@email.com'
    assert response.json()['first_name'] == 'Lucas'
    assert response.json()['last_name'] == 'Balbueno'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '(111)-111-1111'

# Testa o endpoint PUT /users/user/update_password com dados válidos.
# Fluxo do teste:
# 1. Envia uma requisição com a senha atual correta e uma nova senha
# 2. O endpoint verifica se a senha atual está correta
# 3. Se válida, atualiza para a nova senha hashed
# 4. Retorna status 204 (No Content) indicando sucesso sem retornar dados
def test_change_password_success(test_user):
    # Faz requisição PUT enviando senha atual e nova senha no corpo da requisição
    response = client.put("/users/user/update_password", json={
        "password": "testpassword",     # Senha atual (deve coincidir com a senha da fixture)
        "new_password": "newpassword"   # Nova senha que será definida
    })

    # Verifica se retorna status 204 No Content
    assert response.status_code == status.HTTP_204_NO_CONTENT

# Testa o endpoint PUT /users/user/update_password com senha atual incorreta.
# Fluxo do teste:
# 1. Envia uma requisição com senha atual INCORRETA
# 2. O endpoint verifica a senha atual usando bcrypt
# 3. Como não confere, retorna erro 401 Unauthorized
# 4. Inclui mensagem de erro específica no JSON de resposta
def test_change_password_invalid_current_password(test_user):
    # Faz requisição PUT com senha atual propositalmente incorreta
    response = client.put("/users/user/update_password", json={
        "password": "wrong_password",   # Senha incorreta (não confere com "testpassword")
        "new_password": "newpassword"   # Nova senha (será ignorada devido ao erro)
    })

    # Verifica se retorna status 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Verifica se a mensagem de erro é exatamente a esperada
    assert response.json() == {'detail': 'Error on password change'}

# Testa o endpoint PUT /users/user/update_phone_number/{phone_number} com sucesso.
# Fluxo do teste:
# 1. Envia requisição PUT com novo número de telefone na URL (path parameter)
# 2. O endpoint atualiza diretamente o campo phone_number do usuário
# 3. Retorna status 204 No Content indicando sucesso
def test_change_phone_number_success(test_user):
    # Faz requisição PUT onde o novo número de telefone vai na URL como parâmetro
    # O "2222222222" substitui o placeholder {phone_number} na rota
    response = client.put("/users/user/update_phone_number/2222222222")

    # Verifica se retorna status 204 No Content
    assert response.status_code == status.HTTP_204_NO_CONTENT