import pytest

# Testa igualdade e desigualdade básicas
def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1

# Verifica se objetos são instâncias de tipos específicos
def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)

# Testa valores booleanos e comparações que retornam boolean
def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False

# Testa tipos de dados
def test_type():
    assert type('Hello' is str)
    assert type('World' is not int)

# Testa comparações numéricas (maior e menor que)
def test_greater_and_less_than():
    assert 7 > 3
    assert 4 < 10

# Testa operações com listas:
def test_list():
    num_list = [1, 2, 3, 4, 5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    # all() - retorna True se todos os elementos são verdadeiros
    assert all(num_list)
    # any() - retorna True se pelo menos um elemento é verdadeiro
    assert not any(any_list)

# Modelo simples representando um estudante
# Classe com construtor inicializado
class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

# As fixtures são uma funcionalidade fundamental do pytest que permite criar dados ou objetos reutilizáveis de forma independente e idêntica para cada teste.
# Decorator que cria um objeto reutilizável para testes
@pytest.fixture
def default_employee():
    return Student('John', 'Doe', 'Computer Science', 3)

# Testa se o objeto Student foi inicializado corretamente usando a fixture
def test_person_initialization(default_employee):
    assert default_employee.first_name == 'John', 'First name should be John'
    assert default_employee.last_name == 'Doe', 'Last name should be Doe'
    assert default_employee.major == 'Computer Science'
    assert default_employee.years == 3