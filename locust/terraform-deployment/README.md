# Terraform Deployment for the Locust Framework

This Terraform deployment is designed to create a distributed testing environment using Locust. The environment consists of virtual machines (VMs) on Azure, where one VM acts as the Locust Master and multiple VMs serve as Locust Workers. The deployment is automated using GitHub Actions or Jenkins, ensuring the setup is executed, the load tests are run, and the environment is cleanly destroyed after tests are completed.

# Directory Structure

```
terraform-deployment
├── CI
│   ├── Jenkinsfile
│   └── terraform-locust-deployment-workflow.yml
├── README.md (This File)
├── dockerfile (Dockerfile to build the deployer image)
├── docker-compose-yml (Docker Compose file with Master and Worker Service)
├── locust-infra.tf (Main Terraform Configuraton File)
└── scripts
    ├── create-locust-infra.sh (Script that logins into Azure and executes Terraform)
    └── locust-infra-setup.sh (Script that will be runned inside every VM, installing and running Locust)
```

# Usage Github Actions

## 1. Copy the Workflow File to Your Repository
Copy the terraform-locust-deployment-workflow.yml file into the .github/workflows/ directory of your repository. This will enable GitHub Actions to recognize and execute the workflow.

## 2. Copy the Script upload_to_reporter.sh Inside the Locust File to Your Workflow
Place the upload_to_reporter.sh script (located in locust/scripts/upload_to_reporter.sh) in an appropriate directory within your repository, such as a scripts folder. Ensure that it is referenced correctly in your workflow file.

## 3. Define Required Variables in Your Repository
In your repository settings, go to 'Secrets' and add the following environment variables:
AZURE_CLIENT_ID: Your Azure Client ID.
AZURE_CLIENT_SECRET: Your Azure Client Secret.
AZURE_TENANT_ID: Your Azure Tenant ID.
These will be used by the Terraform script to authenticate and execute actions in your Azure environment.

## 4. Create Your Locust Scenario in the Scenarios Folder
Create a scenarios folder if it doesn't exist. Write your test scenarios in this folder. These are Python scripts defining user behavior for load testing with Locust. More info [here](https://confluence.tid.es/pages/viewpage.action?pageId=73025608#id-[QPMPerf]EstrategiayMetodolog%C3%ADa-Dise%C3%B1odeescenariosdePerformanceconLocust)

## 5. Run the Workflow
Push your changes to the repository or manually trigger the workflow from the GitHub Actions tab.
The workflow will now execute, deploying your Terraform infrastructure and running the Locust tests as defined.

## Requirements

The only requirement needed in the Runner is Docker and Docker Compose

# Usage Jenkins

TBD
