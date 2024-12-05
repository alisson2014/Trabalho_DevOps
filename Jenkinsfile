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
