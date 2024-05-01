import settings
import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.setsockopt(zmq.IPV6, 1)
socket.connect(settings.zeromq_address)

try:
    socket.send_json({"command": "ping"})
    event = socket.poll(2000)
    if event == 0:
        print("Poll timeout")
        exit(1)
    data = socket.recv_json(flags=zmq.NOBLOCK)
    assert data.get("status") == "ok"
    print("pong")
    exit(0)
except Exception as e:
    exit(1)
