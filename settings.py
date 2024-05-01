import os

lasqa_channel = "channel-chat:8845069"
roadhouse_channel = "channel-chat:6367818"
zhmil_channel = "channel-chat:6639759"

vk_channel = os.getenv("VK_CHANNEL", lasqa_channel)

worker_idle_timeout_seconds = int(os.getenv("IDLE_TIMEOUT_MIN", "15")) * 60
randomize_votes = os.getenv("RANDOMIZE_VOTES", "false") == "true"

zeromq_address = os.getenv("RPC_ADDRESS", "tcp://127.0.0.1:4242")
