pipeline {
    agent any
    
    environment {
        VERSION = "${env.BUILD_ID}"
        DOCKERHUB_REPO = "khaira23/registration-app"
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                url: 'https://github.com/Khaira11/registration-app.git'
            }
        }
        
        stage('Setup') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip3 install -r requirements.txt
                python3 -c "import flask; print('✅ Core imports successful!')"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker image..."
                docker build -t ${DOCKERHUB_REPO}:${VERSION} .
                echo "Docker build completed successfully!"
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                sh '''
                echo "Testing Docker image..."
                docker run --rm ${DOCKERHUB_REPO}:${VERSION} python -c "import flask; print('✅ Docker image works!')"
                '''
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'Docker_hub',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    )]) {
                        sh '''
                        echo "Logging into Docker Hub..."
                        echo $DOCKERHUB_PASSWORD | docker login -u $DOCKERHUB_USERNAME --password-stdin
                        
                        echo "Pushing image to Docker Hub..."
                        docker push ${DOCKERHUB_REPO}:${VERSION}
                        
                        echo "Tagging as latest..."
                        docker tag ${DOCKERHUB_REPO}:${VERSION} ${DOCKERHUB_REPO}:latest
                        docker push ${DOCKERHUB_REPO}:latest
                        
                        echo "Logging out from Docker Hub..."
                        docker logout
                        '''
                    }
                }
            }
        }
        
        stage('Cleanup Local Images') {
            steps {
                sh '''
                echo "Cleaning up local Docker images..."
                docker rmi ${DOCKERHUB_REPO}:${VERSION} || true
                docker rmi ${DOCKERHUB_REPO}:latest || true
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo "Pipeline completed successfully! ✅"
            echo "Docker image pushed to: ${DOCKERHUB_REPO}:${VERSION}"
        }
        failure {
            echo "Pipeline failed! ❌"
        }
    }
}
