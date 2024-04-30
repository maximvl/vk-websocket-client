import settings
import zerorpc

client = zerorpc.Client(timeout=3)
client.connect(settings.rpc_address)

try:
    assert client.ping() == True
    exit(0)
except Exception as e:
    exit(1)
