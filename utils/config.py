import os
from dotenv import load_dotenv
load_dotenv()

# LINE Bot
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')

# LINE Notify
NOTIFY_TOKEN = os.getenv('NOTIFY_TOKEN')