import os

lasqa_channel = "channel-chat:8845069"
roadhouse_channel = "channel-chat:6367818"
zhmil_channel = "channel-chat:6639759"

vk_channel = os.getenv("VK_CHANNEL", lasqa_channel)

control_queue_name = "control"
votes_queue_name = "votes"

worker_idle_timeout_seconds = int(os.getenv("IDLE_TIMEOUT_MIN", "15")) * 60

randomize_votes = os.getenv("RANDOMIZE_VOTES", "false") == "true"
