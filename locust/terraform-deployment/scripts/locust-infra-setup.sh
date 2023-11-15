#!/bin/bash

# Update package list and install dependencies
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list and install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io 

DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker

if [ "$1" == "worker" ]; then
  sudo docker compose -f /home/adminuser/locust/docker-compose.yml up -d --scale locustMaster=0 --scale locustWorker=2
  echo "Locust Worker is running on port 8089."
  exit 0
elif [ "$1" == "master" ]; then
  sudo docker compose -f /home/adminuser/locust/docker-compose.yml up -d --scale locustMaster=1 --scale locustWorker=0
  echo "Locust master is running on port 8089."
fi
