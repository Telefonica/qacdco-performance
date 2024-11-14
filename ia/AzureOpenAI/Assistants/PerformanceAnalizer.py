import time
from openai import AzureOpenAI
from IPython.display import clear_output
import json
import os

client = AzureOpenAI(
    # Replace with your Azure OpenAI .env file
    # The .env file should contain the following variables:
    api_key="cf56ce6ffb6d418f9c56793b9e7830ed",
    api_version="2024-10-01-preview",
    azure_endpoint="https://chatgpt-qa-licenses.openai.azure.com/"
)

start_time = time.time()

# Replace with your assistant ID from .env file
assistant_id = "asst_yZPBn70DcKVh4YCRdYP10KVr"

# Paso 1: Listar todos los archivos del asistente
files = client.files.list()  # Esto debería obtener todos los archivos actualmente disponibles en el asistente

# Paso 2: Borrar todos los archivos
for file in files:  # Itera directamente sobre el objeto files
    file_id = file.id  # Accede a la ID del archivo directamente como un atributo
    client.files.delete(file_id)  # Eliminar el archivo usando su ID
    print(f"Archivo con ID {file_id} eliminado.")

# Paso 3: Subir un nuevo archivo
file_path = "locust_results.csv"  # Especifica la ruta de tu nuevo archivo
with open(file_path, "rb") as f:
    content = client.files.create(file=f, purpose="assistants")  # Ajusta el propósito si es necesario
    print(f"Nuevo archivo subido con ID {content.id}")

# Paso 4: Añadir el fichero subido al assistant
client.beta.assistants.update(
    assistant_id = assistant_id,
    tool_resources = {"code_interpreter":{"file_ids":[content.id]}}
)
print(f"Archivo con ID {content.id} añadido al asistente.")



# Create an assistant
'''assistant = client.beta.assistants.create(
    name="Data Visualization",
    instructions=f"Sigue estos pasos:",
                 f"Selecciona todos los eventos cuyo label contenga AccountDashboardModuleAgent.1.getAccountModules_success y  Settings.3.getUserSettingsConfig  coge los datos de las columas timeStamp y elapsed",
                 f"sacame una grafica donde cada label sea una linea, con puntos (no me unas los puntos con lineas), del numero de eventos por segundo del punto anterior a lo largo del tiempo(timeStamp), agrupamelo en intervalos de 5 segundos , quitando los primeros 2 minutos de la prueba,  En el eje x pon la fecha en oblicuo para evitar que se solapen. En el eje y calculame los TPS(transacciones por segundo) teniendo en cuenta que lo has agrupado en intervalos de 5 segundos. Los colores de cada label son rojo y verde.",
                 f"sacame otra grafica con las mismas carateristicas del punto anterior, pero donde se calcule el percentil 90 del campo elapsed agrupado cada 5 segundos. El campo elapsed esta en milisegundos. Dibuja ademas  una linea horizontal de puntos de color rojo para p90=1000, este será un umbral maximo del p90 que tendras en cuenta en las conclusiones finales. Añade esta linea a la leyenda con el titulo de umbal maximo.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106Preview"  # You must replace this value with the deployment name for your model.
)'''

assistant = client.beta.assistants.retrieve(assistant_id)
print(assistant.model_dump_json(indent=2))

# Create a thread
thread = client.beta.threads.create()
print(thread)

# Add a user question to the thread
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
    content="Ejecuta"
)
thread_messages = client.beta.threads.messages.list(thread.id)
print(thread_messages.model_dump_json(indent=2))

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Ejecuta instrucciones"
)

print(f'Status: {status}')
print("Elapsed time: {} minutes {} seconds".format(int((time.time() - start_time) // 60),
                                                   int((time.time() - start_time) % 60)))
print(f'Resultado del prompt {messages.model_dump_json(indent=2)}')
data = json.loads(messages.model_dump_json(indent=2))  # Load JSON data into a Python object

os.makedirs("img", exist_ok=True)
os.makedirs("docs", exist_ok=True)

for message in data["data"]:
    # Verificar si hay contenido que tenga un tipo `image_file` con un `file_id`
    for content_item in message.get("content", []):
        if content_item.get("type") == "image_file" and "image_file" in content_item:
            file_id = content_item["image_file"]["file_id"]
            content = client.files.content(file_id)
            filename = f"img/{file_id}.png"
            content.write_to_file(filename)
            print(f"Imagen guardada en: {filename}")

    # Verificar si hay un archivo adjunto en `attachments`
    if "attachments" in message and message["attachments"]:
        for attachment in message["attachments"]:
            file_id = attachment["file_id"]
            # Obtener el contenido del archivo usando el cliente y guardarlo
            content = client.files.content(file_id)
            filename = f"docs/{file_id}.docx"
            content.write_to_file(filename)
            print(f"Documento guardado en: {filename}")