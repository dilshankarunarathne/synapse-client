import requests

LOG_SERVER_URL = 'http://localhost:3000/log'


def log(message):
    message = "[Client-Core] " + message
    try:
        response = requests.post(LOG_SERVER_URL, json={'message': message},
                                 headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print('Log message sent:', response.json())
    except requests.exceptions.RequestException as error:
        print('Error sending log message:', error)
