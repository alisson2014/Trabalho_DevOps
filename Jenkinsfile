pipeline {
    agent any

    stages {
        stage('Download do Código') {
            steps {
                build {
                    git branch: "main",  url: 'https://github.com/alisson2014/Trabalho_DevOps.git'
                }
            }
        }

        stage('Rodar Testes') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'
                sh 'pip install -r requirements.txt'
                sh 'pytest src/test_app.py'
            }
        }

        stage('Build e Deploy') {
            steps {
                sh 'docker-compose up --build -d'
            }
        }
    }

    post {
        success {
            // Enviar notificação de sucesso
            echo 'Pipeline finalizada com sucesso!'
        }
        failure {
            // Enviar notificação de falha
            echo 'Pipeline falhou!'
        }
    }
}