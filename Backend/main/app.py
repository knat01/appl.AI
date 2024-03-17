from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Function to query GPT model
def query_gpt(prompt, model="text-davinci-003"):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 150
    }

    response = requests.post(f"https://api.openai.com/v1/engines/{model}/completions",
                             headers=headers, json=data)

    if response.status_code == 200:
        return response.json()['choices'][0]['text'].strip()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Endpoint to interact with GPT
@app.route('/api/gpt/query', methods=['POST'])
def gpt_query():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    response = query_gpt(prompt)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
