import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco de dados em memória para testes
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Cria todas as tabelas no banco de dados de teste
        yield client
        with app.app_context():
            db.drop_all()  # Remove todas as tabelas após os testes

def test_nao_deve_trazer_nada(client):
    response = client.get('/alunos')
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 0 

def test_adicionar_aluno_e_verificar_salvamento(client):
    new_aluno = {
        "nome": "João",
        "sobrenome": "Silva",
        "turma": "1A",
        "disciplinas": "Matemática, Física",
        "ra": "12345"
    }
    response = client.post('/alunos', json=new_aluno)
    assert response.status_code == 201
    assert response.json['message'] == 'Aluno adicionado com sucesso!'

    alunos = client.get('/alunos')
    assert alunos.status_code == 200
    assert isinstance(alunos.json, list)
    assert len(alunos.json) == 1 