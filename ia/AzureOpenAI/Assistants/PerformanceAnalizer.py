import time
import json
import os
from openai import AzureOpenAI
from IPython.display import clear_output


class AzureAssistantManager:
    """
    Manages Azure OpenAI Assistant operations such as file handling,
    assistant updates, thread creation, and execution monitoring.
    """

    def __init__(self, api_key, api_version, azure_endpoint, assistant_id):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        self.assistant_id = assistant_id
        self.start_time = time.time()

    def list_and_delete_files(self):
        """
        Lists all files associated with the assistant and deletes them.
        """
        files = self.client.files.list()
        for file in files:
            file_id = file.id
            self.client.files.delete(file_id)
            print(f"File with ID {file_id} deleted.")

    def upload_file(self, file_path, purpose="assistants"):
        """
        Uploads a new file to Azure OpenAI for a specific purpose.
        :param file_path: Path to the file to be uploaded.
        :param purpose: Purpose of the uploaded file (default: 'assistants').
        :return: Uploaded file object.
        """
        with open(file_path, "rb") as f:
            content = self.client.files.create(file=f, purpose=purpose)
            print(f"New file uploaded with ID {content.id}")
            return content

    def associate_file_with_assistant(self, file_id):
        """
        Associates an uploaded file with the assistant.
        :param file_id: ID of the file to be associated.
        """
        self.client.beta.assistants.update(
            assistant_id=self.assistant_id,
            tool_resources={"code_interpreter": {"file_ids": [file_id]}},
        )
        print(f"File with ID {file_id} added to the assistant.")

    def execute_assistant(self, labels, percentile):
        """
        Creates and executes a thread to run the assistant.
        :return: Thread ID for the execution.
        """
        assistant = self.client.beta.assistants.retrieve(self.assistant_id)
        print(assistant.model_dump_json(indent=2))

        thread = self.client.beta.threads.create()
        print(f"Thread created: {thread.id}")

        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""
                Ignora las labels y el percentil que tienes en las instrucciones por defecto, y ejecuta con los siguientes parámetros:
                - Labels: '{labels}'
                - Percentil: '{percentile}'
            """
        )
        thread_messages = self.client.beta.threads.messages.list(thread.id)
        print(thread_messages.model_dump_json(indent=2))

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )
        self.monitor_execution(thread.id, run.id)
        print(f'Resultado del prompt {run.model_dump_json(indent=2)}')
        return thread.id  # Return the thread ID for later use.

    def monitor_execution(self, thread_id, run_id):
        """
        Monitors the execution of an assistant run.
        :param thread_id: ID of the thread.
        :param run_id: ID of the run.
        """
        status = "running"
        while status not in ["completed", "cancelled", "expired", "failed"]:
            time.sleep(5)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run_id
            )
            elapsed_time = time.time() - self.start_time
            print(f"Elapsed time: {elapsed_time // 60:.0f} minutes {elapsed_time % 60:.0f} seconds")
            status = run.status
            print(f"Status: {status}")
            clear_output(wait=True)

    def download_results(self, thread_id):
        """
        Downloads results generated during the assistant run.
        :param thread_id: ID of the thread.
        """
        os.makedirs("img", exist_ok=True)
        os.makedirs("docs", exist_ok=True)

        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        data = json.loads(messages.model_dump_json(indent=2))
        print(f"messages: {messages.model_dump_json(indent=2)}")
        for message in data["data"]:
            for content_item in message.get("content", []):
                if content_item.get("type") == "image_file" and "image_file" in content_item:
                    file_id = content_item["image_file"]["file_id"]
                    content = self.client.files.content(file_id)
                    filename = f"img/{file_id}.png"
                    content.write_to_file(filename)
                    print(f"Image saved at: {filename}")

            if "attachments" in message and message["attachments"]:
                for attachment in message["attachments"]:
                    file_id = attachment["file_id"]
                    content = self.client.files.content(file_id)
                    filename = f"docs/{file_id}.docx"
                    content.write_to_file(filename)
                    print(f"Document saved at: {filename}")


if __name__ == "__main__":
    # Replace with your actual values
    API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
    API_VERSION = "2024-10-01-preview"
    AZURE_ENDPOINT = "https://chatgpt-qa-licenses.openai.azure.com/"
    ASSISTANT_ID = "asst_yZPBn70DcKVh4YCRdYP10KVr"
    LABELS = os.environ("LABELS")
    PERCENTILE = os.environ.get("PERCENTILE", "90")
    # Initialize manager
    manager = AzureAssistantManager(API_KEY, API_VERSION, AZURE_ENDPOINT, ASSISTANT_ID)

    # Step 1: List and delete all files
    manager.list_and_delete_files()

    # Step 2: Upload a new file
    uploaded_file = manager.upload_file("locust_results.csv")

    # Step 3: Associate the uploaded file with the assistant
    manager.associate_file_with_assistant(uploaded_file.id)

    # Step 4: Execute the assistant and monitor execution
    thread_id = manager.execute_assistant(LABELS, PERCENTILE)  # Save the returned thread_id

    # Step 5: Download results using the correct thread ID
    manager.download_results(thread_id=thread_id)
