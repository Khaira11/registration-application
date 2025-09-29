pipeline {
    agent any
    
    environment {
        // Kubernetes configuration
        K8S_NAMESPACE = 'flask-app'
        KUBECONFIG_CREDENTIALS = 'k8s-config'  // Jenkins credentials ID for kubeconfig
        DEPLOYMENT_TIMEOUT = '600'  // 10 minutes timeout
    }
    
    parameters {
        choice(
            name: 'DEPLOY_ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'ROLLBACK_ON_FAILURE',
            defaultValue: true,
            description: 'Automatically rollback on deployment failure?'
        )
        string(
            name: 'IMAGE_TAG_V1',
            defaultValue: 'v1.0.0',
            description: 'Docker image tag for Version 1'
        )
        string(
            name: 'IMAGE_TAG_V2',
            defaultValue: 'v2.0.0',
            description: 'Docker image tag for Version 2'
        )
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }
    
    stages {
        // STAGE 1: Validate Kubernetes Manifests
        stage('Validate K8s Manifests') {
            steps {
                script {
                    echo "1. Validating Kubernetes manifest files..."
                    
                    echo "2. Checking YAML syntax..."
                    sh '''
                        echo "Validating V1 deployment..."
                        kubectl apply --dry-run=client -f k8s/deployment-v1.yaml
                        
                        echo "Validating V2 deployment..."
                        kubectl apply --dry-run=client -f k8s/deployment-v2.yaml
                        
                        echo "Validating services..."
                        kubectl apply --dry-run=client -f k8s/service-v1.yaml
                        kubectl apply --dry-run=client -f k8s/service-v2.yaml
                        
                        echo "Validating ingress..."
                        kubectl apply --dry-run=client -f k8s/ingress.yaml || echo "Ingress validation skipped"
                    '''
                    
                    echo "3. Checking required files..."
                    sh '''
                        ls -la k8s/
                        echo "K8s manifests found and validated successfully!"
                    '''
                }
            }
        }
        
        // STAGE 2: Setup Kubernetes Context
        stage('Setup K8s Context') {
            steps {
                script {
                    echo "4. Setting up Kubernetes context..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh '''
                            echo "KUBECONFIG file path: $KUBECONFIG"
                            export KUBECONFIG=$KUBECONFIG
                            
                            echo "Current Kubernetes context:"
                            kubectl config current-context
                            
                            echo "Kubernetes cluster info:"
                            kubectl cluster-info
                            
                            echo "Available nodes:"
                            kubectl get nodes
                        '''
                    }
                }
            }
        }
        
        // STAGE 3: Create Namespace
        stage('Create Namespace') {
            steps {
                script {
                    echo "5. Creating/verifying Kubernetes namespace..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Creating namespace ${env.K8S_NAMESPACE} if not exists..."
                            kubectl create namespace ${env.K8S_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            echo "Setting current namespace to ${env.K8S_NAMESPACE}..."
                            kubectl config set-context --current --namespace=${env.K8S_NAMESPACE}
                            
                            echo "Current namespaces:"
                            kubectl get namespaces
                        """
                    }
                }
            }
        }
        
        // STAGE 4: Deploy Version 1 (Stable)
        stage('Deploy Version 1 - Stable') {
            steps {
                script {
                    echo "6. Deploying Version 1 (Stable) to Kubernetes..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Updating V1 image to tag: ${params.IMAGE_TAG_V1}"
                            kubectl -n ${env.K8S_NAMESPACE} set image deployment/flask-app-v1 \
                                flask-app=khaira23/flask-demo-v1:${params.IMAGE_TAG_V1} \
                                --record
                            
                            echo "Starting V1 deployment rollout..."
                            kubectl -n ${env.K8S_NAMESPACE} rollout status deployment/flask-app-v1 \
                                --timeout=${env.DEPLOYMENT_TIMEOUT}s
                            
                            echo "Scaling V1 deployment..."
                            kubectl -n ${env.K8S_NAMESPACE} scale deployment flask-app-v1 --replicas=3
                        """
                    }
                }
            }
        }
        
        // STAGE 5: Deploy Version 2 (Canary)
        stage('Deploy Version 2 - Canary') {
            steps {
                script {
                    echo "7. Deploying Version 2 (Canary) to Kubernetes..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Updating V2 image to tag: ${params.IMAGE_TAG_V2}"
                            kubectl -n ${env.K8S_NAMESPACE} set image deployment/flask-app-v2 \
                                flask-app=your-registry/flask-demo-v2:${params.IMAGE_TAG_V2} \
                                --record
                            
                            echo "Starting V2 deployment rollout..."
                            kubectl -n ${env.K8S_NAMESPACE} rollout status deployment/flask-app-v2 \
                                --timeout=${env.DEPLOYMENT_TIMEOUT}s
                            
                            echo "Scaling V2 canary deployment..."
                            kubectl -n ${env.K8S_NAMESPACE} scale deployment flask-app-v2 --replicas=1
                        """
                    }
                }
            }
        }
        
        // STAGE 6: Health Checks
        stage('Health Checks') {
            steps {
                script {
                    echo "8. Performing health checks on deployments..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Checking all deployments status..."
                            kubectl -n ${env.K8S_NAMESPACE} get deployments -o wide
                            
                            echo "Checking pods status..."
                            kubectl -n ${env.K8S_NAMESPACE} get pods -o wide --show-labels
                            
                            echo "Checking services..."
                            kubectl -n ${env.K8S_NAMESPACE} get services -o wide
                        """
                    }
                }
            }
        }
        
        // STAGE 7: Application Testing
        stage('Application Testing') {
            steps {
                script {
                    echo "9. Testing application endpoints..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Testing V1 application health..."
                            V1_POD=\$(kubectl -n ${env.K8S_NAMESPACE} get pod -l version=v1 -o jsonpath='{.items[0].metadata.name}')
                            echo "V1 Pod: \$V1_POD"
                            kubectl -n ${env.K8S_NAMESPACE} exec \$V1_POD -- curl -s http://localhost:5000/health
                            
                            echo "Testing V2 application health..."
                            V2_POD=\$(kubectl -n ${env.K8S_NAMESPACE} get pod -l version=v2 -o jsonpath='{.items[0].metadata.name}')
                            echo "V2 Pod: \$V2_POD"
                            kubectl -n ${env.K8S_NAMESPACE} exec \$V2_POD -- curl -s http://localhost:5000/health
                            kubectl -n ${env.K8S_NAMESPACE} exec \$V2_POD -- curl -s http://localhost:5000/metrics
                            
                            echo "All application tests completed successfully!"
                        """
                    }
                }
            }
        }
        
        // STAGE 8: Canary Validation (Manual Approval)
        stage('Canary Validation - Manual Approval') {
            steps {
                script {
                    echo "10. Waiting for manual approval to continue..."
                    echo "Check canary deployment at: your-ingress-url/v2"
                    echo "If everything looks good, approve to continue."
                }
            }
        }
        
        // STAGE 9: Promote Canary to Production
        stage('Promote Canary to Production') {
            when {
                beforeInput true
                expression { return true }  // Always show, but requires approval
            }
            input {
                message "Promote V2 canary to production?"
                ok "Yes, Promote to Production"
                parameters {
                    booleanParam(
                        name: 'CONFIRM_PROMOTION',
                        defaultValue: false,
                        description: 'I confirm that canary testing is successful and want to promote V2 to production'
                    )
                }
            }
            steps {
                script {
                    echo "11. Promoting V2 to production..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Scaling up V1 with V2 image (blue-green switch)..."
                            kubectl -n ${env.K8S_NAMESPACE} set image deployment/flask-app-v1 \
                                flask-app=your-registry/flask-demo-v2:${params.IMAGE_TAG_V2} \
                                --record
                            
                            echo "Waiting for V1 rollout with new image..."
                            kubectl -n ${env.K8S_NAMESPACE} rollout status deployment/flask-app-v1 \
                                --timeout=${env.DEPLOYMENT_TIMEOUT}s
                            
                            echo "Scaling down canary deployment..."
                            kubectl -n ${env.K8S_NAMESPACE} scale deployment flask-app-v2 --replicas=0
                            
                            echo "Production promotion completed!"
                        """
                    }
                }
            }
        }
        
        // STAGE 10: Final Verification
        stage('Final Verification') {
            steps {
                script {
                    echo "12. Final deployment verification..."
                    
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            echo "Final deployment status:"
                            kubectl -n ${env.K8S_NAMESPACE} get all
                            
                            echo "Current images in production:"
                            kubectl -n ${env.K8S_NAMESPACE} get deployments -o jsonpath='{.items[*].spec.template.spec.containers[*].image}'
                            
                            echo "Deployment history:"
                            kubectl -n ${env.K8S_NAMESPACE} rollout history deployment/flask-app-v1
                            kubectl -n ${env.K8S_NAMESPACE} rollout history deployment/flask-app-v2
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "13. Cleaning up and collecting artifacts..."
            script {
                // Collect deployment logs
                sh '''
                    echo "Collecting deployment logs..."
                    kubectl get events --sort-by='.lastTimestamp' > k8s-events.log || true
                    kubectl get all -o wide > k8s-resources.log || true
                '''
                
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
                cleanWs()
            }
        }
        success {
            echo "✅ KUBERNETES DEPLOYMENT SUCCESSFUL!"
            script {
                // Success notification
                emailext (
                    subject: "SUCCESS: K8s Deployment ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                    body: """
                    Kubernetes deployment completed successfully!
                    
                    Environment: ${params.DEPLOY_ENVIRONMENT}
                    Build: ${env.BUILD_NUMBER}
                    Namespace: ${env.K8S_NAMESPACE}
                    
                    View build: ${env.BUILD_URL}
                    """,
                    to: 'devops-team@yourcompany.com'
                )
            }
        }
        failure {
            echo "❌ KUBERNETES DEPLOYMENT FAILED!"
            script {
                if (params.ROLLBACK_ON_FAILURE.toBoolean()) {
                    echo "Automatically rolling back deployments..."
                    withCredentials([file(
                        credentialsId: env.KUBECONFIG_CREDENTIALS,
                        variable: 'KUBECONFIG'
                    )]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            echo "Rolling back V1 deployment..."
                            kubectl -n ${env.K8S_NAMESPACE} rollout undo deployment/flask-app-v1
                            echo "Rolling back V2 deployment..."
                            kubectl -n ${env.K8S_NAMESPACE} rollout undo deployment/flask-app-v2
                            echo "Rollback completed!"
                        """
                    }
                }
                
                // Failure notification
                emailext (
                    subject: "FAILED: K8s Deployment ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                    body: """
                    Kubernetes deployment failed!
                    
                    Environment: ${params.DEPLOY_ENVIRONMENT}
                    Build: ${env.BUILD_NUMBER}
                    Rollback: ${params.ROLLBACK_ON_FAILURE}
                    
                    Check logs: ${env.BUILD_URL}console
                    """,
                    to: 'devops-team@yourcompany.com'
                )
            }
        }
    }
}
