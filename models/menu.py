from linebot.v3.messaging import (
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    MessageAction
)
import handlers.datahandler as datahandler
import asyncio
from termcolor import cprint


class RichMenuModel:
    async def create_rich_menus(self):
        try:
            # 創建 rich menu 並儲存 ID
            normal_menu_id = await self.create_normal_menu()
            admin_menu_id = await self.create_admin_menu()
            setting_menu_id = await self.create_setting_menu()
            
            cprint(f"Normal Menu ID: {normal_menu_id.rich_menu_id}", "light_grey", "on_dark_grey")
            cprint(f"Admin Menu ID: {admin_menu_id.rich_menu_id}", "light_grey", "on_dark_grey")
            cprint(f"Setting Menu ID: {setting_menu_id.rich_menu_id}", "light_grey", "on_dark_grey")
            
            # 儲存 rich menu ID 到檔案
            save_tasks = [
                datahandler.WriteToJSON("rich_menu_ids.json", "normal", normal_menu_id.rich_menu_id),
                datahandler.WriteToJSON("rich_menu_ids.json", "admin", admin_menu_id.rich_menu_id),
                datahandler.WriteToJSON("rich_menu_ids.json", "settings", setting_menu_id.rich_menu_id)
            ]
            await asyncio.gather(*save_tasks)

            # 上傳圖片
            upload_tasks = [
                self.UploadRichMenuImage(normal_menu_id.rich_menu_id, "menu/image/normal_menu.png"),
                self.UploadRichMenuImage(admin_menu_id.rich_menu_id, "menu/image/admin_menu.png"),
                self.UploadRichMenuImage(setting_menu_id.rich_menu_id, "menu/image/setting_menu.png")
            ]
            await asyncio.gather(*upload_tasks)

            return {
                "normal": normal_menu_id.rich_menu_id,
                "admin": admin_menu_id.rich_menu_id,
                "settings": setting_menu_id.rich_menu_id
            }
        
        except asyncio.TimeoutError:
            cprint("建立 rich menu 超時", "red")
            return None
            
        except Exception as e:
            cprint(e, "red")


    # 創建一般用戶的 rich menu
    async def create_normal_menu(self):
        from api.line_api import LineAPI

        normal_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=843),
            selected=True,
            name="Normal User Menu",
            chat_bar_text="一般選單",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1666, height=843),
                    action=MessageAction(type="message", label="回報", text="回報")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
                    action=MessageAction(type="message", label="輸出", text="輸出")
                )
            ]
        )

        normal_menu_id = await LineAPI().CreateRichMenu(normal_menu)

        return normal_menu_id


    # 創建管理員的 rich menu
    async def create_admin_menu(self):
        from api.line_api import LineAPI

        admin_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=843),
            selected=True,
            name="Admin User Menu",
            chat_bar_text="管理員選單",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                    action=MessageAction(type="message", label="回報", text="回報")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                    action=MessageAction(type="message", label="輸出", text="輸出")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
                    action=MessageAction(type="message", label="設定", text="設定")
                )
            ]
        )

        admin_menu_id = await LineAPI().CreateRichMenu(admin_menu)

        return admin_menu_id



    # 創建管理員的 setting menu
    async def create_setting_menu(self):
        from api.line_api import LineAPI

        setting_menu = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="Admin Setting Menu",
            chat_bar_text="管理員設定選單",
            areas=[
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                    action=MessageAction(type="message", label="暫停排程", text="暫停排程")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                    action=MessageAction(type="message", label="恢復排程", text="恢復排程")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=0, width=834, height=843),
                    action=MessageAction(type="message", label="廣播", text="廣播")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                    action=MessageAction(type="message", label="設定班級", text="設定班級")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=833, y=843, width=833, height=843),
                    action=MessageAction(type="message", label="新增管理員", text="新增管理員")
                ),
                RichMenuArea(
                    bounds=RichMenuBounds(x=1666, y=843, width=834, height=843),
                    action=MessageAction(type="message", label="輸出uid", text="輸出uid")
                ),
            ]
        )

        setting_menu_id = await LineAPI().CreateRichMenu(setting_menu)

        return setting_menu_id


    async def UploadRichMenuImage(self, rich_menu_id, image_path):
        try:
            from api.line_api import LineAPI

            with open(image_path, 'rb') as f:
                await LineAPI().UploadRichMenuImage(
                    rich_menu_id,
                    bytearray(f.read())
                )

            cprint(f"圖片上傳成功: {image_path}", "green", "on_dark_grey")
        
        except Exception as e:
            cprint(e, "red")