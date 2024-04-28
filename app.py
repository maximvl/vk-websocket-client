from vk_chat_reader.controller import Controller
from vk_chat_reader.ws_client import get_websocket_token, start_websocket_client
import pika
import settings
import time


def on_control_message(ch, method, properties, body, controller: Controller):
    print(f"Control message: {body}")
    if body == b"ping":
        controller.start_worker()
        controller.update_ping(int(time.time()))
    elif body == b"stop":
        controller.stop_worker()
    else:
        print(f"Unknown message: {body}")


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=settings.control_queue_name)

    controller = Controller()

    def callback(*args):
        on_control_message(*args, controller=controller)

    channel.basic_consume(
        queue=settings.control_queue_name,
        on_message_callback=callback,
        auto_ack=True,
    )
    print("Staring control loop")
    channel.start_consuming()


if __name__ == "__main__":
    main()
