import os

lasqa_channel = "channel-chat:8845069"
roadhouse_channel = "channel-chat:6367818"
zhmil_channel = "channel-chat:6639759"

vk_channel = os.getenv("VK_CHANNEL", lasqa_channel)

worker_idle_timeout_seconds = int(os.getenv("IDLE_TIMEOUT_MIN", "15")) * 60
randomize_votes = os.getenv("RANDOMIZE_VOTES", "false") == "true"

rabbit_host = os.getenv("RABBIT_HOST", "localhost")
rabbit_user = os.getenv("RABBIT_USER", "guest")
rabbit_pass = os.getenv("RABBIT_PASSD", "guest")
control_queue_name = "control"
votes_queue_name = "votes"
