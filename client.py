import argparse
import json
import os
import threading
import time
import websocket
import base64

from config_parser.config import Config
from logger.web_logger import log
from security.hashing import calculate_hash
from auth.authentication import register_client, acquire_token

config = Config('cfg/client_config.ini')
WS_SERVER_URL = config.get('Server', 'SERVER_URL')

DATA_FILE = 'client_data.json'


def save_client_data(client_id, token):
    with open(DATA_FILE, 'w') as f:
        json.dump({'client_id': client_id, 'token': token}, f)


def load_client_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return None


def authenticate(username, password):
    client_data = load_client_data()
    if client_data:
        return client_data['client_id'], client_data['token']
    client_id = register_client(username, password)
    token = acquire_token(username, password)
    save_client_data(client_id, token)
    return client_id, token


def create_job(payload_path, data_file_path):
    from logger.web_logger import log

    with open(payload_path, 'rb') as payload_file, open(data_file_path, 'rb') as data_file:
        payload = payload_file.read()
        data = data_file.read()

    payload_encoded = base64.b64encode(payload).decode('utf-8')
    data_encoded = base64.b64encode(data).decode('utf-8')

    job_data = {
        'type': 'create_job',
        'payload': payload_encoded,
        'data': data_encoded
    }

    def c_on_message(ws, message):
        log(f"Received message: {message}")
        try:
            response = json.loads(message)
            if response.get("type") == "job_created":
                job_id = response.get("job_id")
                log(f"Job created successfully with job_id: {job_id}")
            else:
                log(f"Unexpected message type: {response.get('type')}")
        except json.JSONDecodeError as e:
            log(f"Error decoding message: {e}")

    def c_on_error(ws, error):
        log(f"Error: {error}")

    def c_on_close(ws, close_status_code, close_msg):
        log(f"Connection closed: {close_status_code} {close_msg}")

    def c_on_open(ws):
        log("Connection established")
        # log(f"Sending job data: {job_data}")
        ws.send(json.dumps(job_data))

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_SERVER_URL,
                                on_open=c_on_open,
                                on_message=c_on_message,
                                on_error=c_on_error,
                                on_close=c_on_close)

    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()
        log("Client terminated")


def on_message(ws, message):
    log(f"Received message: {message}")
    if message.startswith("New job assigned: "):
        job_id = message.split(": ")[1]
        log(f"Processing job: {job_id}")
        result, payload_hash, data_hash = process_job(job_id)
        ws.send(f"Job result: {job_id}: {result}: {payload_hash}: {data_hash}")
    else:
        log(f"Received non-job message: {message}")


def on_error(ws, error):
    log(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    log(f"Connection closed: {close_status_code} {close_msg}")


def on_open(ws):
    log("Connection established")


def process_job(job_id):
    log(f"Job {job_id} is being processed...")
    time.sleep(5)
    result = f"Result of job {job_id}"
    payload_hash = calculate_hash(b"payload data")
    data_hash = calculate_hash(b"data")
    log(f"Job {job_id} completed with result: {result}")
    return result, payload_hash, data_hash


def start_service():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_SERVER_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()
        log("Client terminated")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Synapse Client')
    parser.add_argument('-auth', action='store_true', help='Authenticate the client with the server')
    parser.add_argument('-register', action='store_true', help='Register the client with the server')
    parser.add_argument('-start-service', action='store_true', help='Start the websocket service')
    parser.add_argument('-create-job', action='store_true', help='Create a new job')
    parser.add_argument('-u', '--username', type=str, help='Username for authentication')
    parser.add_argument('-p', '--password', type=str, help='Password for authentication')
    parser.add_argument('-payload', type=str, help='Path for the payload file')
    parser.add_argument('-data', '--data_file_path', type=str, help='Path for the data file')

    args = parser.parse_args()

    if args.auth:
        if not args.username or not args.password:
            parser.error('-auth requires -u/--username and -p/--password')
        client_id, token = authenticate(args.username, args.password)
        log(f"Authenticated with client_id: {client_id} and token: {token}")
    elif args.register:
        if not args.username or not args.password:
            parser.error('-register requires -u/--username and -p/--password')
        from auth.authentication import register_client
        client_id = register_client(args.username, args.password)
        log(f"Registered with client_id: {client_id}")
    elif args.start_service:
        start_service()
    elif args.create_job:
        if not args.payload or not args.data_file_path:
            parser.error('-create-job requires -payload and -data')
        create_job(args.payload, args.data_file_path)
    else:
        print("no arguments specified for the synapse client")
        print("starting client daemon...")
        start_service()