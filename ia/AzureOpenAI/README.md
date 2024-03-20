First you need to create a .env file with the following variables:

```bash

AZURE_OPENAI_API_KEY=sk-xxxxxxxxxxxxxx
ASSISTANT_ID="asst_51JqlsIIkcTftOFCuOWEnO0d"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"

```
run the following commands to start the test (modify absolute path to the assistants folder in your local machine):

```bash
docker build -t performanceanalizer:0.0.1 .
docker rm -f performanceanalizer ;docker  run -v $HOME/git/telefonica/qacdco-performance/ia/AzureOpenAI/Assistants:/app --name performanceanalizer  performanceanalizer:0.0.1


```
These commands will create an image with 2 requests using novum performance test example inside assistant.


