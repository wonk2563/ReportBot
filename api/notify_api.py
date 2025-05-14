import requests
from termcolor import cprint
from utils.config import NOTIFY_TOKEN


# ----------------------------------------------------
# LINE Notify 已於 2025 年 3 月 31 日停止支援
# 若要使用相關功能，請改為使用 Messaging API
# ----------------------------------------------------
# 發送通知到 LINE Notify
# content: 要發送的內容
# ----------------------------------------------------
async def Notify(content):
    url = 'https://notify-api.line.me/api/notify'
    token = NOTIFY_TOKEN
    if token is None:
        cprint('NOTIFY_TOKEN 為空', 'red')
        return
    
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message' : f'{content}'
    }
    
    data = requests.post(url, headers=headers, data=data)