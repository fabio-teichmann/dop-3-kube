# Use the official Jenkins LTS base image
# FROM jenkins/jenkins:lts

# USER root

# # Install necessary tools: kubectl, helm, git, curl
# RUN apt-get update && \
#     apt-get install -y curl git unzip && \
#     curl -LO "https://dl.k8s.io/release/$(curl -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
#     install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
#     rm kubectl && \
#     curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# # Install recommended Jenkins plugins via CLI (optional for minimal setup)
# COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
# RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# # Set ownership back to Jenkins user
# RUN chown -R jenkins:jenkins /var/jenkins_home

# USER jenkins

FROM jenkins/jenkins:lts

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    git \
    unzip \
    gnupg \
    lsb-release \
    software-properties-common
 
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl


# Install Helm (v3)
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# (Optional) Install Docker CLI if you plan to build/push from Jenkins
# RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins

