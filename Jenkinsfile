pipeline {
    agent any

    environment {
        IMAGE_NAME = "odoo-custom"
        NEXUS_URL  = "nexus:8082"
        SONAR_URL  = "http://sonarqube:9000"
        STAGING_NS = "staging"
        PROD_NS    = "production"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                script {
            // Ajoute ces 2 lignes
            env.GIT_BRANCH = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
            echo "Branche : ${env.GIT_BRANCH}"
        }
            }
        }

        stage('Verification Syntaxe Python') {
            steps {
                sh '''
            python3 -m venv .venv
            .venv/bin/pip install flake8 --quiet
            .venv/bin/flake8 . --max-line-length=120 --exclude=.venv
        '''
    } 
     
        }

        stage('Tests Unitaires') {
            steps {
       sh '''
            python3 -m venv .venv
            .venv/bin/pip install pytest --quiet
            .venv/bin/pytest snim_maintenance/tests/ -v        '''
    }
        }

        stage('Analyse SonarQube') {
             steps {
        withSonarQubeEnv('SonarQube') {
            sh '''
                export PATH=$PATH:/opt/sonar-scanner/bin
                sonar-scanner \
                  -Dsonar.projectKey=odoo-custom \
                  -Dsonar.sources=addons \
                  -Dsonar.host.url=http://localhost:9000 \
                  -Dsonar.python.version=3.10
            '''
        }
    }
        }

        stage('Build Image Docker') {
            steps {
                sh """
                    docker build \
                      -t ${NEXUS_URL}/${IMAGE_NAME}:${BUILD_NUMBER} .
                """
            }
        }

        stage('Scan Securite Trivy') {
            steps {
                sh """
                    trivy image --exit-code 0 \
                      --severity HIGH,CRITICAL \
                      ${NEXUS_URL}/${IMAGE_NAME}:${BUILD_NUMBER}
                """
            }
        }

        stage('Push vers Nexus') {
    steps {
        withCredentials([usernamePassword(
            credentialsId: 'nexus-credentials',
            usernameVariable: 'NEXUS_USER',
            passwordVariable: 'NEXUS_PASS'
        )]) {
            sh """
                echo \$NEXUS_PASS | docker login nexus:8082 \
                  --username \$NEXUS_USER --password-stdin
                docker push ${NEXUS_URL}/${IMAGE_NAME}:${BUILD_NUMBER}
            """
        }
    }
}

      stage('Deploy Staging') {
          when { expression { env.GIT_BRANCH == 'develop' } }

    steps {
        sh "minikube image load ${NEXUS_URL}/${IMAGE_NAME}:${BUILD_NUMBER}"
        sh "kubectl create namespace ${STAGING_NS} --dry-run=client -o yaml | kubectl apply -f -"
        sh "kubectl create namespace ${PROD_NS} --dry-run=client -o yaml | kubectl apply -f -"
        sh """
            helm upgrade --install odoo-staging ./helm \
              --namespace ${STAGING_NS} \
              --set image.tag=${BUILD_NUMBER} \
              --timeout 3m
        """
    }
}
        stage('Tests Validation Staging') {
          when { expression { env.GIT_BRANCH == 'develop' } }
    
    steps {
        sh 'sleep 30'
        sh 'curl -f http://192.168.49.2:30069/web/health'
    }
}

    stage('Deploy Production') {
    when { expression { env.GIT_BRANCH == 'main' } }
    steps {
        sh "minikube image load ${NEXUS_URL}/${IMAGE_NAME}:${BUILD_NUMBER}"
        sh """
            helm upgrade --install odoo-prod ./helm \
              --namespace ${PROD_NS} \
              --set image.tag=${BUILD_NUMBER} \
              --set service.nodePort=30070 \
              --atomic --wait --timeout 6m
        """
    }
}
}
    post {
        success {
            echo "✅ Build ${BUILD_NUMBER} déployé avec succès !"
 }
        failure {
            echo "❌ Build ${BUILD_NUMBER} échoué !" 
               sh """
                helm rollback odoo-staging \
                  --namespace ${STAGING_NS} || true
            """
        }
    }
}