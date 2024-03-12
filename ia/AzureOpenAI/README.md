First you need to create a .env file with the following variables:

```bash

AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxxx

```
run the following command to start the test:

```bash
docker-compose --env-file .env -f docker-compose.yaml up -d --force-recreate

```

Use your browser to access the locust web interface at http://localhost:8089

