pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'gopioo/fluid-ai-app'
        DOCKER_CREDENTIALS = '3eba655b-ddff-4738-bbcf-ce339eb78dd0'
        AWS_REGION = 'us-east-1'
        EKS_CLUSTER = 'Fluid-AI-project'
        K8S_NAMESPACE = 'fluid-ai'
        DEPLOYMENT_NAME = 'flask-app'
        CONTAINER_NAME = 'flask-app'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build(
                        "${DOCKER_IMAGE}:${BUILD_NUMBER}",
                        "./app"
                    )
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        "${DOCKER_CREDENTIALS}"
                    ) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Configure AWS / EKS') {
            steps {
                sh '''
                    aws sts get-caller-identity

                    aws eks update-kubeconfig \
                        --region ${AWS_REGION} \
                        --name ${EKS_CLUSTER}

                    kubectl get nodes
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    kubectl set image deployment/${DEPLOYMENT_NAME} \
                        ${CONTAINER_NAME}=${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        -n ${K8S_NAMESPACE}

                    kubectl rollout status deployment/${DEPLOYMENT_NAME} \
                        -n ${K8S_NAMESPACE} \
                        --timeout=180s
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "===== Pods ====="
                    kubectl get pods -n ${K8S_NAMESPACE}

                    echo "===== Services ====="
                    kubectl get svc -n ${K8S_NAMESPACE}

                    echo "===== Deployment ====="
                    kubectl get deployment ${DEPLOYMENT_NAME} \
                        -n ${K8S_NAMESPACE}
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Fluid AI deployment completed successfully!'
        }

        failure {
            echo '❌ Fluid AI deployment failed. Check the Jenkins console output.'
        }
    }
}