# Use the official Jenkins LTS base image
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
    software-properties-common \
    openssh-client && \
    apt-get clean

# Add the Jenkins user's SSH private key (assuming it exists locally at ~/.ssh)
# Ensure to set correct permissions for the key
COPY ~/.ssh/dop_3_jenkins /var/jenkins_home/.ssh/id_rsa
RUN chmod 600 /var/jenkins_home/.ssh/id_rsa

# Add known hosts
RUN mkdir -p /var/jenkins_home/.ssh && \
    ssh-keyscan github.com >> /var/jenkins_home/.ssh/known_hosts && \
    chmod 644 /var/jenkins_home/.ssh/known_hosts
 
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl

# Install Helm (v3)
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# (Optional) Install Docker CLI to build/push from Jenkins
# RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins
ENTRYPOINT ["sh", "-c", "eval $(ssh-agent -s) && ssh-add /var/jenkins_home/.ssh/id_rsa && exec /usr/local/bin/jenkins.sh"]
