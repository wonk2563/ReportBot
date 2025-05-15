from termcolor import cprint
from api.line_api import LineAPI
import handlers.datahandler as datahandler
import handlers.jobhandler as jobhandler
# from api import notify_api


async def handle_event(event):
    try:
        admin_uid = await datahandler.GetAdminUID()
        content = ''
        top = ''
        uid = event.source.user_id
        match event.type:
            case 'message':
                prompts = event.message.text.split('\n')
                top = prompts[0]
                content = event.message.text
                
            case 'postback':
                prompts = event.postback.data.split('\n')
                top = prompts[0]
                content = event.postback.data
                
            case 'follow':
                cprint(f'{uid} follow', "light_blue")
                await LineAPI().ReplyMenutoUser('uid' ,'report' ,event.reply_token)
                
            case _:
                pass
            
        if uid in admin_uid:
            match top:

                # ----------------------------------------------------
                # LINE Notify 已於 2025 年 3 月 31 日停止支援
                # 若要使用相關功能，請改為使用 Messaging API
                # ----------------------------------------------------
                case '廣播':
                    # data = content.split('\n')[1]
                    # await notify_api.Notify(f'{data}')
                    await LineAPI().ReplytoUser(event.reply_token, '廣播功能已關閉，請使用 Messaging API 進行廣播')

                    menu_ids = await datahandler.ReadAllFromJSON("rich_menu_ids.json")
                    await LineAPI().LinkRichMenuToUser(uid, menu_ids["admin"])
                
                case '暫停排程':
                    await jobhandler.Pause_job()
                    await LineAPI().ReplytoUser(event.reply_token, '暫停排程工作成功')
                
                case '恢復排程':
                    await jobhandler.Resume_job()
                    await LineAPI().ReplytoUser(event.reply_token, '恢復排程工作成功')

                case '輸出uid':
                    result = await datahandler.Output_Uid()
                    await LineAPI().ReplytoUser(event.reply_token, result)
                    await LineAPI().LinkRichMenuToUser(uid, menu_ids["admin"])

                case '設定':
                    menu_ids = await datahandler.ReadAllFromJSON("rich_menu_ids.json")
                    await LineAPI().LinkRichMenuToUser(uid, menu_ids["settings"])

                case '設定班級':
                    await LineAPI().ReplyMenutoUser('class' ,'report' ,event.reply_token)

                case _ if 'setclass' in top:
                    prompts = event.postback.data.split('-')
                    class_number = prompts[0]
                    class_name = prompts[1]
                    await datahandler.WriteToJSON("class_data.json", "className", f'{class_name}')
                    await datahandler.WriteToJSON("class_data.json", "classNumber", f'{class_number}')
                    await LineAPI().ReplytoUser(event.reply_token, f'班級設定成功，\n班級名稱：{class_name}\n班級號碼：{class_number}')
                    
                    menu_ids = await datahandler.ReadAllFromJSON("rich_menu_ids.json")
                    await LineAPI().LinkRichMenuToUser(uid, menu_ids["admin"])

                case '新增管理員':
                    await LineAPI().ReplyMenutoUser('admin' ,'report' ,event.reply_token)

                case _ if 'setadmin' in top:
                    prompts = event.postback.data.split('-')
                    new_admin_student = await datahandler.ReadFromJSON("students_data.json", f'{prompts[0]}')
                    result = await datahandler.Set_Admin(new_admin_student['uid'], admin_uid)
                    await LineAPI().ReplytoUser(event.reply_token, result)

                    menu_ids = await datahandler.ReadAllFromJSON("rich_menu_ids.json")
                    await LineAPI().LinkRichMenuToUser(uid, menu_ids["admin"])
                    

        match top:
            case _ if 'setadmin' in top and len(admin_uid) == 0:
                result = await datahandler.Set_Admin(event.source.user_id, admin_uid)
                await LineAPI().ReplytoUser(event.reply_token, result)

            case _ if 'setuid' in top:
                result = await datahandler.Set_Uid(content, event.source.user_id, admin_uid)
                await LineAPI().ReplyMultitoUser(event.reply_token, result)
                
            case '輸出':
                await LineAPI().ReplyMenutoUser('main', token=event.reply_token)
                
            case '回報':
                await LineAPI().ReplyMenutoUser('main', 'report', event.reply_token)
                
            case _ if 'get' in top and 'Non' not in top and 'Total' not in top:
                prompts = event.postback.data.split('-')
                type = prompts[1].replace('Report', '')
                await LineAPI().ReplyMenutoUser(type, token=event.reply_token)
                
            case 'get-nightNonReport':
                reportResult = await datahandler.Get_Nonreport("nightReport", "休假回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-busNonReport':
                reportResult = await datahandler.Get_Nonreport("busReport", "專車回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-vacationNonReport':
                reportResult = await datahandler.Get_Nonreport("vacationReport", "休假規劃")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-closeNonReport':
                reportResult = await datahandler.Get_Nonreport("closeReport", "收假回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-nightTotalReport':
                reportResult = await datahandler.Get_Totalreport("nightReport", "休假回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-busTotalReport':
                reportResult = await datahandler.Get_Totalreport("busReport", "專車回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-vacationTotalReport':
                reportResult = await datahandler.Get_Totalreport("vacationReport", "休假規劃")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case 'get-closeTotalReport':
                reportResult = await datahandler.Get_Totalreport("closeReport", "收假回報")
                await LineAPI().ReplytoUser(event.reply_token, reportResult)
                
            case _ if '休假回報' in top:
                result = await datahandler.Set_data(uid, 'nightReport', content)
                await LineAPI().ReplytoUser(event.reply_token, result)
                
            case _ if '專車回報' in top:
                result = await datahandler.Set_data(uid, 'busReport', content)
                await LineAPI().ReplytoUser(event.reply_token, result)
                
            case _ if '休假規劃' in top:
                result = await datahandler.Set_data(uid, 'vacationReport', content)
                await LineAPI().ReplytoUser(event.reply_token, result)
                
            case _ if '收假回報' in top:
                result = await datahandler.Set_data(uid, 'closeReport', content)
                await LineAPI().ReplytoUser(event.reply_token, result)
                
            case _ if '專車統計' in top:
                totalReport = await datahandler.BusReportAnalysis(event, content)
                await LineAPI().ReplytoUser(event.reply_token ,totalReport)
                
            case 'set-nightReport':
                await LineAPI().ReplySampletoUser(event, uid, '休假回報')
                
            case 'set-busReport':
                await LineAPI().ReplySampletoUser(event, uid, '專車回報', True)
                
            case 'set-vacationReport':
                await LineAPI().ReplySampletoUser(event, uid, '休假規劃')
                
            case 'set-closeReport':
                await LineAPI().ReplySampletoUser(event, uid, '收假回報')
                
            case _:
                pass

    except Exception as e:
        cprint(e, "red")