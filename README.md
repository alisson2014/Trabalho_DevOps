# Trabalho_DevOps

## Alunos

+ Riyuiti Mizuno RA: 22.9016-0
+ Alisson Vinicius Morais de Almeida  RA: 23.9782-6

## Introdução

Neste trabalho implementamos as rotas *GET* e *POST* de alunos no flask, bem como fizemos *testes de unidade* para garantir a integridade do código. Todo o projeto foi desenvolvido usando conceitos de *DEVOPS*, que foi a disciplina do mesmo.

### Tecnologias
Neste projeto usamos as seguintes tecnologias:
- Linux;
- Docker;
- Docker Compose;
- Git;
- GitHub;
- Jenkins;
- Python;

## Inicio

### O arquivo docker-compose.yml foi criado pelo terminal do ubuntu, para que possa configurar os container dentro do projeto.

```
vim docker-compose.yml
```

### Para editar o arquivo docker-compose.yml decidimos editar pelo visual studio code, pois dessa achamos que seria da forma mais fácil de organizar, e implmentar novos codigos dentro dele. Dessa forma, dentro do arquivo foi inserido o seguinte codigo:

```docker-compose.yml
services:
  mariadb:
    build:
      context: ./docker/mariadb
      dockerfile: Dockerfile
    container_name: mariadb_container
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: school_db
      MYSQL_USER: flask_user
      MYSQL_PASSWORD: flask_password

  flask_app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: flask_app_container
    ports:
      - "5000:5000"
    depends_on:
      - mariadb
    environment:
      FLASK_APP: app
      FLASK_ENV: development
      FLASK_DB_HOST: mariadb
      FLASK_DB_USER: flask_user
      FLASK_DB_PASSWORD: flask_password
      FLASK_DB_NAME: school_db

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - flask_app

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    container_name: phpmyadmin_container
    depends_on: 
      - mariadb
    environment:
      PMA_HOST: mariadb
      MYSQL_ROOT_PASSWORD: root_password
    ports: 
      - "3008:80"

  mysqld_exporter:
    image: prom/mysqld-exporter
    environment:
      - DATA_SOURCE_NAME=mysql://flask_user:flask_password@mariadb:3306/school_db
    ports:
      - "9104:9104"
    depends_on:
      - mariadb

volumes:
  db_data:
  grafana_data:
  ```

  ### Decidimos implementar todos os containers necessarios para o projeto, que no caso foi o mariaDB, flask, prometheus, grafana e php. Após isso, criamos a pasta src e dentro dele criamos o arquivo app.py, com os seguintes códigos:

```app.py
# Código principal do Flask (app.py)
import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics
import logging

app = Flask(__name__)

metrics = PrometheusMetrics(app)
# Configuração da chave secreta para sessões
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_secreta'  # Substitua por uma chave segura

# Configuração do banco de dados
if app.config['TESTING']:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco de dados em memória para testes
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados e o AppBuilder
db = SQLAlchemy(app)
appbuilder = AppBuilder(app, db.session)

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Aluno - Definição da tabela 'Aluno' no banco de dados
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    disciplinas = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(50), nullable=False)

def init_db():
    """Função para inicializar o banco de dados"""
    attempts = 5
    for i in range(attempts):
        try:
            with app.app_context():
                db.create_all()  # Inicializa o banco de dados
                # Criar um usuário administrador padrão
                if not appbuilder.sm.find_user(username='admin'):
                    appbuilder.sm.add_user(
                        username='admin',
                        first_name='Admin',
                        last_name='User',
                        email='admin@admin.com',
                        role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
                        password='admin'
                    )
            logger.info("Banco de dados inicializado com sucesso.")
            break
        except OperationalError:
            if i < attempts - 1:
                logger.warning("Tentativa de conexão com o banco de dados falhou. Tentando novamente em 5 segundos...")
                time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
            else:
                logger.error("Não foi possível conectar ao banco de dados após várias tentativas.")
                raise

# Visão do modelo Aluno para o painel administrativo
class AlunoModelView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

# Adicionar a visão do modelo ao AppBuilder
appbuilder.add_view(
    AlunoModelView,
    "Lista de Alunos",
    icon="fa-folder-open-o",
    category="Alunos",
)

# Rota para listar todos os alunos - Método GET
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    output = [{'id': aluno.id, 'nome': aluno.nome, 'sobrenome': aluno.sobrenome, 'turma': aluno.turma, 'disciplinas': aluno.disciplinas, 'ra': aluno.ra} for aluno in alunos]
    return jsonify(output)

# Rota para adicionar um aluno - Método POST
@app.route('/alunos', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    novo_aluno = Aluno(nome=data['nome'], sobrenome=data['sobrenome'], turma=data['turma'], disciplinas=data['disciplinas'], ra=data['ra'])
    db.session.add(novo_aluno)
    db.session.commit()
    logger.info(f"Aluno {data['nome']} {data['sobrenome']} adicionado com sucesso!")
    return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### Após os cógidos, criamos o arquivo requirementes.txt para colocar todas as depencias necessárias para o projeto.
```requirements.txt
pytest==6.2.5
pytest-flask==1.2.0
Flask-Testing==0.8.0
Flask==1.1.4  # Versão compatível com Flask-AppBuilder
Flask-SQLAlchemy==2.4.4  # Extensão do Flask para integração com SQLAlchemy
PyMySQL==0.9.3  # Biblioteca para conexão do Python com o banco de dados MariaDB
Flask-AppBuilder==3.3.0  # Versão compatível com Flask 1.x
Werkzeug==1.0.1  # Versão compatível do Werkzeug para evitar erros de importação
MarkupSafe==2.0.1  # Versão compatível com Jinja2 e Flask
WTForms==2.3.3  # Versão compatível com Flask-AppBuilder que contém o módulo 'compat'
prometheus-flask-exporter==0.18.3
```

### Em seguida, criamos uma pasta docker dentro da raiz, e nela foi criado a pasta mariaDB, dentro dela com o arquivo Dockerfile

```Dockerfile
FROM mariadb:10.5

ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=school_db
ENV MYSQL_USER=flask_user
ENV MYSQL_PASSWORD=flask_password

EXPOSE 3306
```

### Após o banco de dados, foi inserido o comando no terminal para subir os container que foram criados:

```
  docker compose up -d
```

  # Primeiro teste

  ### Depois de verificar os containers, o primeiro teste foi se o "localhost:5000" que foi configurado dentro do container flask-app está funcionando, e deu seguintes resultados:

  ![alt text](.github/assets/image.png)

  ### Em seguida, foi feito o teste dentro da web o "GET", e o "POST" dos alunos está funcionando, para garantir que a mariadb está armazenando os dados inseridos, nesse caso foi feito de forma manual.

  ![alt text](.github/assets/image-1.png)

  # Conclusão

  ### Tivemos um ótimo resultado em poder acessar o "localhost:5000" e armazenamento dos dados dos alunos.

  # Jenkins


  ### Em seguida, decidimos primeiramente criar a pasta Jenkinsfile dentro da raiz, pois nessa pasta vamos verificar as etapas do processo, desde download até deploy da aplicação: 

  ```docker
  pipeline {
    agent any

    stages {
        stage('Download do Código') {
            steps {
                script {
                    git branch: "main",  url: 'https://github.com/alisson2014/Trabalho_DevOps.git'
                }
            }
        }

        stage('Rodar Testes') {
            steps {
                script {
                    sh 'docker compose up -d'
                    sh 'sleep 50' 
                    
                    try {
                        sh 'docker compose exec flask_app pytest'
                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        error "Erro ao rodar testes: ${e.message}"
                        throw e
                    } finally {
                        sh 'docker compose down -v'
                    }
                }
            }
        }

        stage('Build e Deploy') {
            steps {
                sh 'docker compose up --build -d'
            }
        }
    }

    post {
        success {
            echo 'Pipeline finalizada com sucesso!'
        }
        failure {
            echo 'Pipeline falhou!'
        }
    }
}
```

  # Segundo Teste  

  ### Em seguida iremos entra na web com o "localhost:8080" que foi configurado dentro do container do jenkins, acessando na web, iremos utilizar as ferramentas disponíveis dentro do jenkins, nesse caso, iremos utiliar para gerenciar pipeline do projeto. Para isso, inserimos um nome no item, em seguida selecionamoes a opção "Pipeline", pois a pipeline no Jenkins automatiza o processo de integração e entrega contínua (CI/CD), orquestrando etapas como compilação, testes e implantação, depois de selecionado, iremos prosseguidar clicando o botão "Tudo pronto".

  ![alt text](.github/assets/image-3.png)

  ### Dentro da configuração, vamos na opção de definição, e trocamos para "Pipeline scrip from SCM", dentro do "SCM" selecionamoso "GIT", pois dessa forma podemos inserir o repositório do projeto dentro do campo "Repository URL", que no caso, o repósitrio que foi inserido foi esse: "https://github.com/alisson2014/Trabalho_DevOps.git", nas credenciais só é necessário configurar se no caso o repsitório for privado, como nosso caso é público, deixamos a opção "none", e na branch deixamos como /main, para executar dentro da branch principal.

  ![alt text](.github/assets/image-4.png)

  ![alt text](.github/assets/image-5.png)

  ### Para finalizar, foi testado dentro do jenkins os testes unitários, para garantir a integridade do código antes do deploy.

  ![alt text](.github/assets/image-6.png)

  # Promettheus e Grafana

  ### Foi adicionado a pasta grafana e prometheus na raiz do projeto, primeiramente na raiz foi adicionado o arquivo prometheus.yml, ele é o arquivo de configuração do prometheus. Ele define como o Prometheus coleta métricas, de quais alvos (targets) ele as coleta, com que frequência e outras opções essenciais para o funcionamento do sistema.

  ```docker
  global:
  scrape_interval: 15s # Intervalo padrão de coleta de métricas para todos os jobs

scrape_configs:
  - job_name: "prometheus" # Nome do job para o Prometheus
    static_configs:
      - targets: ["localhost:9090"] # Definição do alvo, neste caso o próprio Prometheus

  - job_name: "mysqld_exporter"
    static_configs:
      - targets: ["mysqld_exporter:9104"]
   ```   

   ### Depois adicionamos a pasta grafana dentro da raiz, a pasta do Grafana dentro do Docker é usada para armazenar e organizar as configurações e dados persistentes do Grafana. Isso é importante porque, ao usar contêineres Docker, os dados dentro do contêiner são descartados quando ele é removido. Usar volumes ou montar pastas locais permite que as configurações sejam salvas entre as reinicializações do contêiner.

   ### A tree do grafana ficaria dessa forma:
   ```docker
grafana/
├── dashboards/
│   └── my_dashboard.json        # Dashboards customizados
├── provisioning/
│   ├── datasources/
│   │   └── datasource.yml       # Configurações de fontes de dados
│   ├── dashboards/
│   │   └── dashboard.yml        # Configurações de dashboards
└── Dockerfile_grafanaa                 # Configuração geral do Grafana
```
 + Os dashboards criados, usuários configurados e outras configurações persistem mesmo após o contêiner ser reiniciado ou recriado.

 + As pastas são usadas para carregar automaticamente dashboards e datasources (fontes de dados).

    # Último teste

    ### O primeiro teste foi o acesso dentro do prometheus na web no "localhost:9090".

    ![alt text](.github/assets/image-7.png)

    ### Segundo teste e acessar o grafana, e dentro dela, inserir no "username" admin, "password" admin, para ter acesso dentro do Grafana.

    ![alt text](.github/assets/image-11.png)

    ### Depois de logar, vai na parte esquerda da página, na opção connections, na opção "data source", e procure prometheus e seleciona.

    ![alt text](.github/assets/image-8.png)

    ### Depois de selecionar, insira na "connection" a seguinte url

    ![alt text](.github/assets/image-9.png)

    ### E depois vai na opção save & teste.

    ![alt text](.github/assets/image-10.png)

