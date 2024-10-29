import threading
import time
import websocket
from config_parser.config import Config

config = Config('cfg/client_config.ini')
WS_SERVER_URL = config.get('Server', 'SERVER_URL')


def on_message(ws, message):
    print(f"Received message: {message}")
    if message.startswith("New job assigned: "):
        job_id = message.split(": ")[1]
        print(f"Processing job: {job_id}")
        result = process_job(job_id)
        ws.send(f"Job result: {job_id}: {result}")
    else:
        print("Received non-job message")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print("Connection closed")


def on_open(ws):
    print("Connection established")


def process_job(job_id):
    print(f"Job {job_id} is being processed...")
    time.sleep(5)
    result = f"Result of job {job_id}"
    print(f"Job {job_id} completed with result: {result}")
    return result


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
