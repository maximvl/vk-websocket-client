from multiprocessing import Queue
import time
from typing import Optional
import websocket
import json
import requests
from bs4 import BeautifulSoup
import settings
import random
from queue import Empty
import zmq
from vk_chat_reader.utils import eprint

from vk_chat_reader.types import PingMessage, ChatMessage


websocket_url = (
    "wss://pubsub.live.vkplay.ru/connection/websocket?cf_protocol_version=v2"
)


def start_websocket_client(control_queue: Queue, messages_queue: Queue) -> None:
    token = get_websocket_token()
    last_ping_at = time.time()

    def handle_message(ws, json_message):
        control_message = None
        nonlocal last_ping_at
        try:
            control_message = control_queue.get_nowait()
        except Empty:
            pass

        if isinstance(control_message, PingMessage):
            last_ping_at = control_message.last_ping_at

        if int(time.time()) - last_ping_at > settings.worker_idle_timeout_seconds:
            eprint("Closing websocket due to inactivity")
            ws.close()

        parsed_message = on_message(ws, json_message)
        if parsed_message:
            if settings.randomize_votes:
                parsed_message["message"] = str(random.randint(1, 5))
            # return
            eprint(f"Sent {parsed_message}")
            messages_queue.put(parsed_message)


    def on_open(ws):
        send_initial_messages(token, ws)

    eprint("Starting websocket client")
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=handle_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        header={"Origin": "https://live.vkplay.ru"},
    )
    ws.run_forever(
        reconnect=5,
        skip_utf8_validation=True,
    )
    eprint("Websocket client stopped")

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.IPV6, 1)
    socket.connect(settings.zeromq_client_address)
    socket.send_json({"command": "clear_storage"})
    socket.close()
    context.term()
    eprint("Storage cleaned")


def on_message(ws, json_message) -> Optional[ChatMessage]:
    # eprint(f" -> {json_message}")
    if json_message == b"{}":
        ws.send("{}")
        return None
    return parse_message(json_message)


def parse_message(json_message: str) -> Optional[ChatMessage]:
    message = json.loads(json_message)
    message_data = None
    author_id = None
    author_name = None

    eprint("parsing")
    # eprint(json_message)

    pub_data = message.get("push", {}).get("pub", {}).get("data", {})
    if pub_data.get("type") != "message":
        return None

    message_data = pub_data.get("data", {}).get("data", [])
    text_items = [
        d.get("content")
        for d in message_data
        if d.get("type") == "text" and d.get("content")
    ]

    if not text_items:
        return None

    message_text = "".join([json.loads(item)[0] for item in text_items])

    try:
        int(message_text)
    except Exception:
        return None

    author = pub_data.get("data", {}).get("author", {})
    author_id = author.get("id")
    if not author_id:
        return None

    author_name = author.get("displayName")
    if not author_name:
        return None

    created_at = pub_data.get("data", {}).get("createdAt")
    if not created_at:
        return None

    message_id = pub_data.get("data", {}).get("id")
    if not message_id:
        return None

    return ChatMessage(
        id=message_id,
        username=author_name,
        user_id=author_id,
        message=message_text,
        ts=created_at,
    )


def on_error(ws, error):
    eprint("*** WS Error ***")
    eprint(error)
    eprint("*** WS Error ***")


def on_close(ws, status_code, msg):
    eprint("*** WS Closed ***")
    eprint(status_code)
    eprint(msg)
    eprint("*** WS Closed ***")


def send_initial_messages(token: str, ws) -> None:
    eprint(f"Subscribing to {settings.vk_channel}")

    initial_message = json.dumps(
        {
            "connect": {
                "token": token,
                "name": "js",
            },
            "id": 1,
        }
    )
    ws.send(initial_message)

    subscribe_message = json.dumps(
        {
            "subscribe": {"channel": settings.vk_channel},
            "id": 2,
        }
    )
    ws.send(subscribe_message)


def get_websocket_token() -> str:
    response = requests.get("https://live.vkplay.ru")
    parsed = BeautifulSoup(response.text, "html.parser")
    parsed_config = json.loads(parsed.body.script.text)
    return parsed_config["websocket"]["token"]
