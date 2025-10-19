pipeline {
    agent any
    
    stages {
        stage('Build Docker Image') {
            steps {
                echo '🔨 Building Docker image'
                sh 'docker build -t khaira23/flask-jenkins .'
            }
        }
        
        stage('Login & Push to DockerHub') {
            steps {
                echo '🔐 Logging in to DockerHub'
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh '''
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                        docker push khaira23/flask-jenkins:latest
                    '''
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                echo '🚀 Deploying container...'
                sh '''
                    docker stop flask-app || true
                    docker rm flask-app || true
                    docker run -d --name flask-app -p 5000:5000 khaira23/flask-jenkins:latest
                '''
            }
        }
    }
    
    post {
        always {
            echo '🎉 Pipeline execution completed'
        }
    }
}
