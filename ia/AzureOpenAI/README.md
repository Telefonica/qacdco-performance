First you need to create a .env file with the following variables:

```bash

AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
ASSISTANT_ID="asst_51JqlsIIkcTftOFCuOWEnO0d"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"

```
run the following commands to start the test (modify absolute path to the assistants folder in your local machine):

```bash
docker build -t performanceanalizer:0.0.1 .
docker rm -f performanceanalizer; docker run -v .:/app --name performanceanalizer -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY docker.tuenti.io/qsys/performanceanalizer:0.0.1

```
where $AZURE_OPENAI_API_KEY must be defined in your environment variables.
These commands will create an image with 2 requests using Novum performance test example inside assistant.


