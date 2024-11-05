import argparse
import json
import os
import threading
import time
import websocket
import base64

from compiler.main import run_job
from config_parser.config import Config
from logger.web_logger import log
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
        log(f"Connection closed")

    def c_on_open(ws):
        log("Connection established")
        log(f"Sending job data: {json.dumps(job_data)[:50]}")
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
    log(f"Received message")
    if message.startswith("JOB:"):
        parts = message.split("|SEP|")
        job_data = {}
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                job_data[key.strip()] = value.strip()

        job_id = job_data.get("JOB")
        creator = job_data.get("CREATOR")
        leader = job_data.get("LEADER")
        data = job_data.get("DATA")
        payload = job_data.get("PAYLOAD")

        log(f"Processing job: {job_id} from creator: {creator}")
        result = _process_job(job_id, data, payload)
        # TODO hash result, payload and data
        ws.send(f"RESULT:{job_id}:{result}")
    else:
        log(f"Received non-job message: {message}")


def _process_job(job_id, data, payload):
    log(f"Job {job_id} is being processed")

    result = run_job(payload, data)

    log(f"Job {job_id} completed")
    return result


def on_error(ws, error):
    log(f"Error WS: {error}")


def on_close(ws, close_status_code, close_msg):
    log(f"Connection closed")


def on_open(ws):
    log("Connection established")


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
