# dop-3-kube
Simple consumer/producer setup with RabbitMQ deployed in a local Kubernetes cluster with integrated Jenkins CI/CD pipeline.


# Implementation steps

I will follow the following steps to realize this project:

1. set up Kubernetes cluster with application &rarr; foundation and target of other components
2. install Helm in cluster and configure (for deployment automation)
3. set up Jenkins and connect to Kubernetes (allows deployments)
4. set up container registry
5. configure Jenkins pipeline(s)
6. monitor and optimize (optional)

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

> [!NOTE]
> For this project, Jenkins is run outside the Kubernetes cluster in a Docker container.



### Setup

Build and run Jenkins:
```bash
docker build -t <registry_username>/jenkins_dop_3:latest ./jenkins/
docker run -d <registry_username>/jenkins_dop_3:latest
```

The CI pipeline needs a place to store built Docker images before deploying them. Once, Jenkins is running (locally), we need to ensure Jenkins has access (e.g., through SSH keys or access tokens) to GitHub and the image repository (I used DockerHub) for the automated builds. To do this, we need to access Jenkins via web browser and complete the setup: set up  credentials under "Manage Credentials".

When that is in place, the pieces can come together.

### :bulb: Learnings

| :o: Issue | :mag_right: Source | :white_check_mark: Solution |
| :---- | :----- | :------- |
| Jenkins unable to connect to GitHub although tokens in place | Jenkins container did not have access to the SSH files (stored locally) | Manually copied SSH files over to container;<br>Adjusted Dockerfile to copy over file automatically for subsequent runs | 
| Jenkins job unable to run `kubectl` scripts | Missing files in Jenkins container for local Minikube setup | 2 ways to deal with it:<br>1. Use a cloud Kubernetes `kubeconfig` (safer way BUT this project is not using cloud resources);<br>2. make Minikube files available to Jenkins and adjust `kubeconfig` accordingly |
| Jenkins unable to access local Minikube cluster to set up namespace | Unknown | Stopped investigating this issue (see below) |

> [!IMPORTANT]
> I strategically stopped developing this project as the only missing component was for Jenkins to successfully connect to my local Minikube cluster. I had experienced similar issue for different setups, so this might be as well linked to some local variable. The overall link between Jenkins, Helm and Kubernetes is completed.
