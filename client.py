import websocket
import threading
import time
import json

# WebSocket server URL
WS_SERVER_URL = "ws://localhost:8080/ws"

def on_message(ws, message):
    print(f"Received message: {message}")
    # Check if the message is in JSON format
    if message.startswith("New job assigned: "):
        job_id = message.split(": ")[1]
        print(f"Processing job: {job_id}")
        # Add your job processing logic here
        process_job(job_id)
    else:
        print("Received non-job message")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection established")

def process_job(job_id):
    # Simulate job processing
    print(f"Job {job_id} is being processed...")
    time.sleep(5)  # Simulate a delay for job processing
    print(f"Job {job_id} completed")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_SERVER_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # Run WebSocket in a separate thread
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ws.close()
