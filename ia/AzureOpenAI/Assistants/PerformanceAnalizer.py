import time
import os
from openai import AzureOpenAI
from IPython.display import clear_output
from dotenv import load_dotenv
import json

load_dotenv()

client = AzureOpenAI(
    # Replace with your Azure OpenAI .env file
    # The .env file should contain the following variables:
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint="https://chatgpt-qa-licenses.openai.azure.com/"
)


start_time = time.time()

# Replace with your assistant ID from .env file
assistant_id = os.environ["ASSISTANT_ID"]

# Create an assistant
'''assistant = client.beta.assistants.create(
    name="Data Visualization",
    instructions=f"Analiza todo el fichero csv y saca una lista seleccionable por el usuario con todos los eventos unicos de la columna label."
                 f"Despues pediras al usuario que seleccione los eventos que desea "
                 f"De todos los eventos previamente seleccionados sacarás una grafica donde el eje X es la columna timestamp en formato epoch en milisegundos, y el eje y es columna elapsed en milisegundos"
                 f"La grafica debera ser con puntos"
                 f"Añade una leyenda en la grafica con cada nombre",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106Preview"  # You must replace this value with the deployment name for your model.
)'''

assistant = client.beta.assistants.retrieve(assistant_id)

print(assistant.model_dump_json(indent=2))

thread = client.beta.threads.create()
print(thread)


message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Ejecuta"
)

thread_messages = client.beta.threads.messages.list(thread.id)
print(thread_messages.model_dump_json(indent=2))

# Run the assistant
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  #instructions="Ejecuta"
)


status = run.status
print(status)

while status not in ["completed", "cancelled", "expired", "failed"]:
    time.sleep(5)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                       int((time.time() - start_time) % 60)))
    status = run.status
    print(f'Status: {status}')
    clear_output(wait=True)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

print(f'Status: {status}')
print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                   int((time.time() - start_time) % 60)))
print(messages.model_dump_json(indent=2))
# Run the assistant

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="2 y 4"
)
thread_messages = client.beta.threads.messages.list(thread.id)
print(thread_messages.model_dump_json(indent=2))

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Sacame las graficas en dark mode y agrupame el eje x en intervalos de 5 segundos y "
               "calculas el percentil 95 de ese intervalo y no me contabilices el primer minuto"
)


status = run.status
print(status)

while status not in ["completed", "cancelled", "expired", "failed"]:
    time.sleep(5)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                       int((time.time() - start_time) % 60)))
    status = run.status
    print(f'Status: {status}')
    clear_output(wait=True)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

print(f'Status: {status}')
print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                   int((time.time() - start_time) % 60)))
print(messages.model_dump_json(indent=2))
data = json.loads(messages.model_dump_json(indent=2))  # Load JSON data into a Python object
image_file_id = data['data'][0]['content'][0]['image_file']['file_id']

print(image_file_id)
content = client.files.content(image_file_id)

image = content.write_to_file("load_test_account.png")

