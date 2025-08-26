pipeline {
    agent any
    
    environment {
        VERSION = "${env.BUILD_ID}"
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
                docker build -t khaira23/registration-app:${VERSION} .
                echo "Docker build completed successfully!"
                '''
            }
        }
        
        stage('Test Docker Image') {
            steps {
                sh '''
                echo "Testing Docker image..."
                docker run --rm khaira23/registration-app:${VERSION} python -c "import flask; print('✅ Docker image works!')"
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
        }
        failure {
            echo "Pipeline failed! ❌"
        }
    }
}
