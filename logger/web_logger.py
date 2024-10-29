import requests
from config_parser.config import Config

config = Config('cfg/client_config.cfg')
LOG_SERVER_URL = config.get('Logging', 'LOG_SERVER_URL')


def log(message):  # TODO add client id to log message
    print(message)
    message = "[Client-Core] " + message
    try:
        response = requests.post(LOG_SERVER_URL, json={'message': message},
                                 headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print('Log message sent:', response.json())
    except requests.exceptions.RequestException as error:
        print('Error sending log message:', error)
