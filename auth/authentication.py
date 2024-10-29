import requests

from config_parser.config import Config
from logger.web_logger import log

config = Config('cfg/client_config.ini')

AUTHZ_SERVER_URL = config.get('Server', 'AUTHZ_SERVER_URL')
USERNAME = config.get('Credentials', 'USERNAME')
PASSWORD = config.get('Credentials', 'PASSWORD')


def register_client():
    url = f"{AUTHZ_SERVER_URL}/register"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        client_id = response.json().get('client_id')
        log(f"Client registered successfully with client_id: {client_id}")
        return client_id
    except requests.exceptions.RequestException as error:
        log(f"Error registering client: {error}")
        raise


def acquire_token():
    url = f"{AUTHZ_SERVER_URL}/aqquire-token"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        token = response.json().get('token')
        log(f"Token acquired successfully: {token}")
        return token
    except requests.exceptions.RequestException as error:
        log(f"Error acquiring token: {error}")
        raise
