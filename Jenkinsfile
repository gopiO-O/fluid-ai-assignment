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
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
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
                    def dockerImage = docker.build(
                        "${DOCKER_IMAGE}:${BUILD_NUMBER}",
                        "./app"
                    )

                    env.BUILT_IMAGE = "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    def dockerImage = docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}")

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
                        --name ${EKS_CLUSTER} \
                        --kubeconfig ${KUBECONFIG}

                    kubectl get nodes
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    echo "===== Applying Kubernetes manifests ====="

                    kubectl apply \
                        -f k8s/flask-deployment.yaml \
                        -n ${K8S_NAMESPACE}

                    echo "===== Updating image ====="

                    kubectl set image deployment/${DEPLOYMENT_NAME} \
                        ${CONTAINER_NAME}=${DOCKER_IMAGE}:${BUILD_NUMBER} \
                        -n ${K8S_NAMESPACE}

                    echo "===== Waiting for rollout ====="

                    kubectl rollout status \
                        deployment/${DEPLOYMENT_NAME} \
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

                    echo "===== Probes ====="
                    kubectl describe deployment ${DEPLOYMENT_NAME} \
                        -n ${K8S_NAMESPACE} | grep -A 15 -E "Liveness|Readiness|Startup" || true
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
