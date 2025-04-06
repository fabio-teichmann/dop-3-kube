pipeline {
  agent any

  environment {
    IMAGE_TAG = ""
    COMPONENTS = "producer,consumer"
    HELM_DIR = "helm/"
    DOCKER_USER = "fabioteichmann"
    NAMESPACE = "kube-project-1"
    KUBECONFIG_CREDENTIALS_ID = "kubeconfig-jenkins"
  }

  stages {
    stage("Checkout") {
      steps {
        checkout([$class: 'GitSCM',
          branches: [[name: '*/main']],
          userRemoteConfigs: [[
            url: 'git@github.com:fabio-teichmann/dop-3-kube.git',
            credentialsId: 'github-ssh'
          ]]
        ])
        script {
            env.IMAGE_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
        }
      }
    }
    
    stage('Prepare Kubernetes Namespace') {
      steps {
        withEnv(["KUBECONFIG=/var/jenkins_home/.kube/config"]) {
            script {
              sh """
                # Create namespace if it doesn't exist (idempotent)
                kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE
              """
            }
        }

        // withCredentials([file(credentialsId: "${env.KUBECONFIG_CREDENTIALS_ID}", variable: 'KUBECONFIG')]) {
        //   script {
        //     sh """
        //       # Create namespace if it doesn't exist (idempotent)
        //       kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE
        //     """
        //   }
        // }
      }
    }

    stage("Build and Push Image") {
        steps {
            script {
              def components = env.COMPONENTS.split(",")

              withCredentials([usernamePassword(
                  credentialsId: 'dockerhub-creds',
                  usernameVariable: 'DOCKER_USER',
                  passwordVariable: 'DOCKER_PASS'
                  )]){
                  
                    components.each { ->
                    def image = "${DOCKER_USER}/${comp}:${IMAGE_TAG}"

                    // build & push
                    sh """
                        docker build -t ${image} src/${comp}/
                        docker push ${image}
                    """
                  }
                } 
            }
        }
    }

    stage('Deploy with Helm') {
        steps {
            withCredentials([file(credentialsId: "${env.KUBECONFIG_CREDENTIALS_ID}", variable: 'KUBECONFIG')]) {
                sh "export KUBECONFIG=$KUBECONFIG"

                script {
                    def components = env.COMPONENTS.split(",")

                    components.each { comp ->
                        sh """
                        helm upgrade --install $comp $HELM_DIR/$comp \
                            --namespace $NAMESPACE \
                            --values $HELM_DIR/common-values.vaml
                            --set image.repository=$DOCKER_USER/$comp \
                            --set image.tag=$IMAGE_TAG
                        """
                    }
                    // Deploy RabbitMQ separately
                    sh """
                        helm upgrade --install rabbitmq bitnami/rabbitmq \
                        --namespace $NAMESPACE \
                        --values $HELM_DIR/common-values.vaml
                    """
                }
            }
        }
    }
  }
}

