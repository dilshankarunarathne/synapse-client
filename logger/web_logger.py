import requests
import json
import os

from config_parser.config import Config

config = Config('cfg/client_config.ini')

LOG_SERVER_URL = config.get('Logging', 'LOG_SERVER_URL')

DATA_FILE = 'client_data.json'


def load_client_id():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            client_data = json.load(f)
            return client_data.get('client_id')
    return None


def log(message):
    client_id = load_client_id()
    if client_id:
        message = f"[Client-ID: {client_id}] {message}"
    else:
        message = "[Client-ID: Unregistered] " + message

    print(message)
    message = "[Client-Core] " + message.strip()
    try:
        response = requests.post(LOG_SERVER_URL, json={'message': message},
                                 headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        if response.content:
            try:
                print('Log message sent:', response.json())
            except json.JSONDecodeError as error:
                print('Error decoding log server response:', error)
        else:
            print('Log message sent: No content in response')
    except requests.exceptions.RequestException as error:
        print('Error sending log message:', error)
    except json.JSONDecodeError as error:
        print('Error decoding log server response:', error)
