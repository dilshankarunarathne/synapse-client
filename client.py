import threading
import time

import websocket

from auth.authentication import register_client, acquire_token
from config_parser.config import Config
from logger.web_logger import log
from security.hashing import calculate_hash

config = Config('cfg/client_config.ini')
WS_SERVER_URL = config.get('Server', 'SERVER_URL')

client_id = register_client()
token = acquire_token()


def on_message(ws, message):
    print(f"Received message: {message}")
    if message.startswith("New job assigned: "):
        job_id = message.split(": ")[1]
        print(f"Processing job: {job_id}")
        result, payload_hash, data_hash = process_job(job_id)
        ws.send(f"Job result: {job_id}: {result}: {payload_hash}: {data_hash}")
    else:
        print("Received non-job message")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")
    log(f"Connection closed: {close_status_code} {close_msg}")


def on_open(ws):
    print("Connection established")
    log("Connection established")  # TODO add client id to log message


def process_job(job_id):
    print(f"Job {job_id} is being processed...")
    time.sleep(5)
    result = f"Result of job {job_id}"
    payload_hash = calculate_hash(b"payload data")
    data_hash = calculate_hash(b"data")
    print(f"Job {job_id} completed with result: {result}")
    return result, payload_hash, data_hash


if __name__ == "__main__":
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
