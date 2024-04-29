from flask import Flask, request, jsonify
from openai import OpenAI
import os
import json
import requests


# Load OpenAI credentials
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
client = OpenAI(api_key=OPEN_AI_API_KEY)

app = Flask(__name__)

# Function to upload file to OpenAI
def upload_file_to_openai(file_storage):
    # Convert FileStorage to bytes
    file_bytes = file_storage.read()

    response = client.files.create(file=file_bytes, purpose="assistants")
    return response.id

def download_file(file_id):
    file_response = client.files.retrieve(file_id)
    file_url = file_response.url
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download file: {response.status_code}")



# Function to create an assistant
def create_latex_resume_assistant():
    assistant = client.beta.assistants.create(
        name="LaTeX Resume Creator",
        instructions="Convert the provided resume into a LaTeX format.",
        model="gpt-4-1106-preview",
        tools=[{"type": "code_interpreter"}]
    )
    return assistant.id

# Function to generate LaTeX resume
def generate_latex_resume(file_id, assistant_id):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Here is a resume, please convert it into LaTeX format.",
        file_ids=[file_id]
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    # Polling for run completion
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        print("Run Status:", run.status)

    # Retrieve the Messages with the LaTeX resume
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("Messages Response:", messages)
    return messages

# Adjusted Flask route to match existing application
@app.route('/images', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        file = request.files['image']

        # Upload file to OpenAI
        file_id = upload_file_to_openai(file)

        # Create Assistant
        assistant_id = create_latex_resume_assistant()

        # Generate LaTeX resume
        messages_response = generate_latex_resume(file_id, assistant_id)

        # Extract relevant information from messages
        latex_file_id = None
        for message in messages_response.data:
            if message.file_ids:
                latex_file_id = message.file_ids[0]
                break

        if latex_file_id:
            # Download the LaTeX file
            latex_content = download_file(latex_file_id)
            # You might want to save this content to a file or handle it differently depending on your use case

            return jsonify(resume=latex_content)
        else:
            return jsonify(error="LaTeX file not generated"), 400
    else:
        return jsonify(error='No image provided'), 400



if __name__ == '__main__':
    app.run(port=8080, debug=True)

