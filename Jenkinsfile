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

        stage('Construir Containers') {
            steps {
                sh 'docker compose down -v'
                sh 'docker compose build'
            }
        }

        stage('Rodar Testes') {
            steps {
                sh 'docker compose exec flask_app pytest src/test_app.py'
            }
        }

        stage('Build e Deploy') {
            steps {
                sh 'docker compose up -d'
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
