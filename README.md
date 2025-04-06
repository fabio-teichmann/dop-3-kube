# dop-3-kube
Simple consumer/producer setup with RabbitMQ deployed in a local Kubernetes cluster with integrated Jenkins CI/CD pipeline.


# Implementation steps

I will follow the following steps to realize this project:

1. set up Kubernetes cluster with application &rarr; foundation and target of other components
2. install Helm in cluster and configure (for deployment automation)
3. set up Jenkins and connect to Kubernetes (allows deployments)
4. set up container registry
5. configure Jenkins pipeline(s)
6. set up webhooks for automated builds
7. monitor and optimize (optional)

## Setting up the cluster
The consumer and producer components are using the implementation of [this repo](https://github.com/avielb/rmqp-example/tree/master), since the focus of this project is in setting up the environment and less in implementing the application itself. Nonetheless, to understand application and its behavior / limits, I will look into Rabbit MQ in detail.

### Rabbit MQ
The queue will be run (for starters) as a node in the cluster. To do that, we will need the following configurations:

- deployment
- service
- persistent volume (local deployment with Minikube)
- persistent volume claim

The persistent volume will ensure that data sent to the queue will not be lost in case the node goes down.


### Consumer / Producer
To use the provided images (see linked repo above), we need to push them to a **Container Registry** in order for Kubernetes to use them. Once the images are available in the registry, we can start creating the Kubernetes configuration files (`.yaml`).


### :bulb: Learnings

| :o: Issue | :mag_right: Source | :white_check_mark: Solution |
| :---- | :----- | :------- |
| Name or service not known | Producer trying to connect to Rabbit MQ via (cluster) service name that did not coincide | Corrected the service name re-applied config |
| `pika.exceptions.ProbableAuthenticationError` | Credentials passed through in the cluster base64 encoded while the producer file (`.py`) tried to connect with clear values | Replaced hard-coded credentials in producer to pull from environment and decode the base64 encoding |
| Incorrect padding | Base64 encoded secrets need to be padded by `=` to have length multiple of 4 | Needed to replace the secret config file |
| Incorrect padding (persisted) | Decoding in producer pod raised an error | Kubernetes automatically decodes secrets when passed down as environment variables to a pod |



## Helm
Helm will simplify the configuration of our cluster (also at scale). Changes in the configuration file can propagate into the cluster without the need to change individual configuration files (`.yaml`). For this project we will keep the 3 components (RabbitMQ, Consumer, Producer) in 3 separate charts for cleaner and more extendible `values.yaml` files.

To use Helm in our cluster we need to install it and create a Helm chart for each component as a base:

```
# create Helm chart
helm create {component_name}
```

Once the configuration is created we create a release:
```
helm upgrade --install {component_name} ./helm/{component_name}
```

### :bulb: Learnings

| :o: Issue | :mag_right: Source | :white_check_mark: Solution |
| :---- | :----- | :------- |
| Cannot reference values from helm chart | config `.yaml` files were kept in separate folder | 2 ways to deal with this:<br>1. move configs to `/templates` folder<br>2. use a post-install helm hook<br>I will move configs for now |
| Shared configurations not dynamic enough (need to maintain in too many places) | Several helm-charts need common config values | Store shared values in `common-values.yaml` and feed into `helm upgrade --install ...` command. |
| Go marshal error when installing helm-chart | Field in environment variables not type string | Write specific instructions to Helm: `"{{ ... }}"` to indicate string |



## Jenkins

Jenkins is the CI/CD orchestrator, and we need it before automating builds and deployments.
It will need access to the Kubernetes cluster and the container registry.

### Setup

Deploy Jenkins inside Kubernetes:
```sh
helm repo add jenkins https://charts.jenkins.io
helm repo update
helm install jenkins jenkins/jenkins --set controller.serviceType=LoadBalancer
```
Retrieve the admin password:
```sh
kubectl exec --namespace default -it svc/jenkins -c jenkins -- cat /run/secrets/chart-admin-password
```
Access Jenkins via web browser and complete setup.


### Connect to Kubernetes
Jenkins needs to communicate with Kubernetes to deploy applications.
This step ensures Jenkins has proper permissions.

Create a Service Account for Jenkins in Kubernetes:
```sh
kubectl create serviceaccount jenkins
kubectl create clusterrolebinding jenkins-binding --clusterrole=cluster-admin --serviceaccount=default:jenkins
```
Retrieve the Token to Add to Jenkins Credentials:
```sh
kubectl get secret $(kubectl get sa jenkins -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode
```
Add the Token to Jenkins under Manage Jenkins → Manage Credentials → Kubernetes Cluster Credentials.

## Container Registry
The CI pipeline needs a place to store built Docker images before deploying them.
Kubernetes will pull images from this registry.

I will use Docker Hub for this project.

Add credentials to Jenkins under Manage Credentials.


## Configure Jenkins Pipelines
The infrastructure is ready, so we can now define the automation logic.
The pipeline will pull code, build the app, push an image, and deploy it using Helm.

Steps:

Create a Jenkinsfile in your Git repository:
groovy
Copy
Edit
pipeline {
    agent any
    environment {
        IMAGE_NAME = "my-app"
        IMAGE_TAG = "v${env.BUILD_NUMBER}"
        REGISTRY = "registry.example.com"
    }
    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/user/repo.git'
            }
        }
        stage('Build & Test') {
            steps {
                sh 'mvn clean test'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh "docker build -t $REGISTRY/$IMAGE_NAME:$IMAGE_TAG ."
            }
        }
        stage('Push Image to Registry') {
            steps {
                sh "docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
            }
        }
        stage('Deploy with Helm') {
            steps {
                sh """
                helm upgrade --install my-release ./helm-chart \
                    --set image.tag=$IMAGE_TAG \
                    --set image.repository=$REGISTRY/$IMAGE_NAME
                """
            }
        }
    }
}
Commit and push it to Git.

## Set Up Webhooks for Automatic Builds
This ensures Jenkins pipelines trigger automatically on new Git commits.

Steps:

In GitHub/GitLab, go to repository settings → Webhooks.
Set the webhook URL to Jenkins:
perl
Copy
Edit
http://<jenkins-url>/github-webhook/
Enable Push events.


## Monitor and Optimize (Optional)
Once everything works, monitoring helps detect issues and improve performance.

Steps:

Set up logging in Kubernetes:
```sh
kubectl logs -f <pod-name>
```
