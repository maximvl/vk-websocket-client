from vk_chat_reader.controller import Controller
from vk_chat_reader.storage import Storage
from vk_chat_reader.ws_client import get_websocket_token, start_websocket_client
import settings
import time
import zerorpc


class RPCServer:
    controller: Controller
    storage: Storage

    def __init__(self) -> None:
        self.controller = Controller()
        self.storage = Storage()

    def get_messages(self, reader_id: str, ts_from: int):
        print(f"fetching messages for {reader_id}, since {ts_from}")
        self.controller.start_worker()
        new_messages = self.controller.read_all_messages()
        self.storage.add_messages(new_messages)
        messages = self.storage.get_unread_messages(reader_id, ts_from)
        return messages

    def reset_reader(self, reader_id: str):
        print(f"resetting messages for {reader_id}")
        self.storage.reset_reader(reader_id)
        return True

    def clear_storage(self):
        print(f"cleaning storage")
        self.storage.clear()
        return True

    def ping(self):
        return True


def main():
    print(f"Staring RPC server on {settings.rpc_address}")
    server = zerorpc.Server(RPCServer())
    server.bind(settings.rpc_address)
    try:
        server.run()
    except Exception as e:
        print(e)
    server.close()


if __name__ == "__main__":
    main()
