import requests
import json
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def streaming_chat_completion_service(base_url, question):
    url = f"{base_url}chat/chat_completion/"
    access_token = os.getenv("ACCESS_TOKEN")
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    example_config = {
        "lambot_id": "9f6ba95b-7f89-4187-8fe8-25ced48c5fce",
        "messages": [
            {"role": "user", "content": question},
        ],
    }

    response_stream = requests.post(
        url, data=json.dumps(example_config), headers=headers, stream=True
    )

    if response_stream.status_code != 200:
        print(f"Error: Received status code {response_stream.status_code}")
        return

    for event in response_stream.iter_content(chunk_size=128):
        if event:
            try:
                data = json.loads(event.decode("utf-8"))
                chunk = data.get("chunk", "")
                print(chunk, end="", flush=True)
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream chat completion response.")
    parser.add_argument("--question", type=str, required=True, help="The question to ask Quality LamBot.")
    args = parser.parse_args()

    BASE_URL = "http://127.0.0.1:8000/"

    streaming_chat_completion_service(BASE_URL, args.question)