FROM debian:bullseye-slim

COPY --from=hashicorp/terraform:1.5.0 /bin/terraform /usr/local/bin/terraform

ARG AZURE_CLI_REPO=bullseye
ARG AZURE_CLI_VERSION=2.38.0-1~bullseye

RUN apt-get update && apt-get install openssh-client -y
RUN apt-get install -y --no-install-recommends ca-certificates curl apt-transport-https gnupg && \
    curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null && \
    echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ ${AZURE_CLI_REPO} main" | tee /etc/apt/sources.list.d/azure-cli.list && \
    apt-get update && \
    apt-get install -y azure-cli=${AZURE_CLI_VERSION} && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY locust/ .
RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -q -N ""

CMD az login --service-principal --username $AZURE_CLIENT_ID --password $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID && bash scripts/create-locust-infra.sh
