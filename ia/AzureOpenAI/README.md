First you need to create a .env file with the following variables:

```bash

AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
ASSISTANT_ID="asst_51JqlsIIkcTftOFCuOWEnO0d"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"

```
run the following command to start the test:

```bash
docker-compose --env-file .env -f docker-compose.yaml up -d --force-recreate

```

Use your browser to access the locust web interface at http://localhost:8089

