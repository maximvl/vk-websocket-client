from vk_chat_reader.controller import Controller
from vk_chat_reader.storage import Storage
from vk_chat_reader.ws_client import get_websocket_token, start_websocket_client
from vk_chat_reader.utils import eprint
import settings
import time
import zmq.asyncio
import asyncio
import json



class RPCServer:
    controller: Controller
    storage: Storage

    def __init__(self) -> None:
        self.controller = Controller()
        self.storage = Storage()

    def get_messages(self, client_id: str, ts_from: int):
        eprint(f"fetching messages for {client_id}, since {ts_from}")
        self.controller.start_worker()
        new_messages = self.controller.read_all_messages()
        self.storage.add_messages(new_messages)
        messages = self.storage.get_unread_messages(client_id, ts_from)
        return messages

    def reset_client(self, client_id: str):
        eprint(f"resetting messages for {client_id}")
        self.storage.reset_reader(client_id)
        return True

    def clear_storage(self):
        eprint(f"cleaning storage")
        self.storage.clear()
        return True

    def process_message(self, msg: dict) -> dict:
        command = msg.get("command")
        match command:
            case "ping":
                return {"status": "ok"}
            case "get_messages":
                client_id = msg.get("client_id")
                ts_from = msg.get("ts_from")
                if not client_id or not ts_from or not isinstance(ts_from, int):
                    return {"status": "error", "message": "client_id and ts_from are required"}
                messages = self.get_messages(client_id=client_id, ts_from=ts_from)
                return {"status": "ok", "messages": messages}
            case "reset_client":
                client_id = msg.get("client_id")
                if not client_id:
                    return {"status": "error", "message": "client_id is required"}
                self.reset_client(client_id=client_id)
                return {"status": "ok"}
            case "clear_storage":
                self.clear_storage()
                return {"status": "ok"}
            case _:
                return {"status": "error", "message": "unknown command"}


async def main():
    server = RPCServer()
    eprint(f"Staring ZMQ server on {settings.zeromq_address}")
    zeromq_context = zmq.asyncio.Context()
    sock = zeromq_context.socket(zmq.REP)
    sock.setsockopt(zmq.IPV6, 1)
    sock.bind(settings.zeromq_address)

    while True:
        str_msg = await sock.recv_string()
        try:
            msg = json.loads(str_msg)
            reply = server.process_message(msg)
        except Exception as e:
            eprint(f"Exception: f{str(e)}")
            reply = {"status": "error", "message": str(e)}
        await sock.send_string(json.dumps(reply))

    sock.close()
    zeromq_context.term()


if __name__ == "__main__":
    asyncio.run(main())
