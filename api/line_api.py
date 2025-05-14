from linebot.v3.webhook import WebhookParser 
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    AsyncMessagingApiBlob,
    Configuration,
    ReplyMessageRequest,
    TextMessage
)
from termcolor import cprint
import handlers.datahandler as datahandler
from models.menu import RichMenuModel
from utils.config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN


class LineAPI:
    def __init__(self):
        self.config = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
        self.async_api_client = AsyncApiClient(self.config)
        self.line_bot_api = AsyncMessagingApi(self.async_api_client)
        self.line_bot_blob_api = AsyncMessagingApiBlob(self.async_api_client)
        self.parser = WebhookParser(CHANNEL_SECRET)


    # ----------------------------------------------------
    # 將 Rich Menu 連結到使用者
    # user_id: 使用者 ID
    # rich_menu_id: Rich Menu ID
    # ----------------------------------------------------
    async def LinkRichMenuToAllUser(self):

        # 如果 menu_ids["normal"] 或 menu_ids["admin"] 為空，則創建新的 rich menu
        menu_ids = {
            "normal": "",
            "admin": ""
        }
        menu_ids = await datahandler.ReadAllFromJSON("rich_menu_ids.json")

        if menu_ids['normal'] == '' or menu_ids['admin'] == '':
            # 創建 rich menus
            menu_ids = await RichMenuModel().create_rich_menus()
            cprint("Rich menus 創建完成", "green", "on_dark_grey")

        else:
            # 如果 rich menu 已存在，則不需要重新創建
            cprint("Rich menus 已存在，不需要重新創建", "yellow")
        
        datas = await datahandler.ReadAllFromJSON("students_data.json")

        # 為所有用戶設定對應的 rich menu
        if menu_ids['normal'] != '' or menu_ids['admin'] != '':
            cprint("為所有用戶設定對應的 rich menu 中...", "yellow")

            for key in datas:
                uid = datas[key]['uid']
                if uid:
                    if datas[key]['isAdmin']:
                        await self.LinkRichMenuToUser(uid, menu_ids["admin"])
                    else:
                        await self.LinkRichMenuToUser(uid, menu_ids["normal"])

            cprint("為所有用戶設定對應的 rich menu 完成", "green", "on_dark_grey")


    async def LinkRichMenuToUser(self, uid, menu_id):
        await self.line_bot_api.link_rich_menu_id_to_user(uid, menu_id)


    async def CreateRichMenu(self, menu):
        menu_id = await self.line_bot_api.create_rich_menu(menu)

        return menu_id
    

    async def UploadRichMenuImage(self, menu_id, image):
        await self.line_bot_blob_api.set_rich_menu_image(
                rich_menu_id = menu_id,
                body = image,
                _headers={'Content-Type': 'image/png'}
            )


    # ----------------------------------------------------
    # 回傳 回報範例內容 給使用者
    # uid: 用戶的 UID
    # alt: 回報範例內容的標題
    # isBus: 是否為專車回報
    # ----------------------------------------------------
    async def ReplySampletoUser(self, event ,uid ,alt ,isBus = False):
        datas = await datahandler.ReadAllFromJSON("students_data.json")
        for key in datas.keys():
            if datas[f'{key}']['uid'] == uid:
                id = key
                name = datas[f'{key}']['name']
                if not isBus:
                    await self.ReplytoUser(event.reply_token, f'{alt}\n{id} {name}：')
                else:
                    await self.ReplytoUser(event.reply_token, f'{alt}\n{id} {name}：放假（）收假（）')
                
                break


    # ----------------------------------------------------
    # 回傳訊息給使用者
    # token: 用戶的回覆令牌
    # text: 要回傳的訊息內容
    # ----------------------------------------------------
    async def ReplytoUser(self, token ,text):
        msg = TextMessage(text=text)

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=token,
                messages=[msg]
            )
        )


    # ----------------------------------------------------
    # 回傳 FlexMessage Menu 給使用者
    # 這裡的 menuName 和 menuType 參數可以根據需要進行調整
    # menuName: 菜單名稱
    # menuType: 菜單類型（output 輸出、report 回報）
    # token: 用戶的回覆令牌
    # ----------------------------------------------------
    async def ReplyMenutoUser(self, menuName = '' ,menuType = 'output',token = None):
        menu_message = await datahandler.GetFlexMessage(menuName ,menuType)
        
        await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=token,
                    messages=[menu_message]
                )
        )


    # ----------------------------------------------------
    # 回傳多重訊息給使用者
    # token: 用戶的回覆令牌
    # messages: 要回傳的訊息內容列表
    # ----------------------------------------------------
    async def ReplyMultitoUser(self, token ,messages):
        await self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=token,
                    messages=messages
                )
        )