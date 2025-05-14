import json
import copy
from linebot.v3.messaging import (
    TextMessage,
    FlexMessage,
    FlexContainer
)
from termcolor import cprint


# 從JSON中讀出對應 keyword 的資料
# data = ReadFromJSON("xx.json","keyword")
async def ReadFromJSON(fileName:str,dataName:str):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        data = dataR[dataName]
        fileR.close()
        return data
        
# 從JSON中讀出與輸入 uid 相同的資料
# data = ReadFromJSONwithID("xx.json","UID")
async def ReadFromJSONwithUID(fileName:str,UID:str):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        fileR.close()
        for key in dataR.keys():
            if dataR[key]['uid'] == UID:
                return dataR[key]
        return None
        
# 讀出JSON中所有資料
# data = ReadAllFromJSON("xx.json")
async def ReadAllFromJSON(fileName:str):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        data = json.load(fileR)
        fileR.close()
        return data
                
# 將資料複寫進JSON
# WriteToJSON("xx.json",ID,data)
async def WriteToJSON(fileName:str,dataName:str,data):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        dataR[dataName] = data
    with open(fileName,mode='w') as fileW:
        json.dump(dataR,fileW,indent=4,ensure_ascii=True)
        fileW.close()
                
# 將資料複寫進 JSON 與輸入 uid 相同的資料
# WriteToJSONwithID("xx.json",ID,data)
async def WriteToJSONwithUID(fileName:str,UID:str,data):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        fileR.close()
        for key in dataR.keys():
            if dataR[key]['uid'] == UID:
                dataR[key] = data
    with open(fileName,mode='w') as fileW:
        json.dump(dataR,fileW,indent=4,ensure_ascii=True)
        fileW.close()


# 將資料從JSON中移除
# RemoveFromJSON("xx.json",ID)
async def RemoveFromJSON(fileName:str,dataName:str):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        fileR.close()
        del dataR[dataName]
    with open(fileName,mode='w') as fileW:
        json.dump(dataR,fileW,indent=4,ensure_ascii=True)
        fileW.close()
                
# 將JSON中的特定資料設為空白
# SetDataEmptyJSON("xx.json",ID)
async def SetDataEmptyJSON(fileName:str,dataName:str):
    with open(fileName,mode='r',encoding='utf8') as fileR:
        dataR = json.load(fileR)
        fileR.close()
        dataR[dataName] = ""
    with open(fileName,mode='w') as fileW:
        json.dump(dataR,fileW,indent=4,ensure_ascii=True)
        fileW.close()


# 從 JSON 中讀出所有的 admin uid
# admin_uid = GetAdminUID("xx.json")
async def GetAdminUID():
    with open("students_data.json", mode='r', encoding='utf8') as fileR:
        dataR = json.load(fileR)
        fileR.close()
        admin_uid = []
        for key in dataR.keys():
            if dataR[key]['isAdmin']:
                admin_uid.append(dataR[key]['uid'])

    return admin_uid


# 獲取學生資料並生成 FlexMessage 按鈕列表
# data: 按下按鈕回傳的資料
# sutdents_data = GetContentsFromStudents(data)
async def GetContentsFromStudents(data):
    sutdents_data = await ReadAllFromJSON("students_data.json")
    contents = []
    content = {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": "",
                    "data": "",
                    "displayText": ""
                },
                "style": "secondary"
            }
        ],
        "margin": "lg"
    }

    for key in sutdents_data.keys():
        content["contents"][0]["action"]["label"] = f'{key} {sutdents_data[key]["name"]}'
        content["contents"][0]["action"]["data"] = f'{key}-{data}'
        content["contents"][0]["action"]["displayText"] = f'{key} {sutdents_data[key]["name"]}'
        contents.append(copy.deepcopy(content))

    return contents


# 檢查 uidlist_report.json 內容是否存在，若不存在則創建
# CreateIdListFile()
async def CreateIdListFile():
    studentsData = await ReadAllFromJSON("students_data.json")
    datas = await ReadAllFromJSON("menu/uidlist_report.json")

    first_student_id = list(studentsData.keys())[0]
    first_student_name = studentsData[first_student_id]["name"]

    # 判斷若 contents 為空或 contents 第一個按鈕的 label 與第一位學生的名字不同
    if len(datas["body"]["contents"]) == 0 or first_student_name not in datas["body"]["contents"][0]["contents"][0]["action"]["label"]:
        datas["body"]["contents"] = await GetContentsFromStudents('setuid')
        await WriteToJSON("menu/uidlist_report.json", "body", datas["body"])

        cprint("將 students 資料加入 uidList 完成", "green", "on_dark_grey")


# 檢查 adminlist_report.json 內容是否存在，若不存在則創建
# CreateAdminIdListFile()
async def CreateAdminIdListFile():
    studentsData = await ReadAllFromJSON("students_data.json")
    datas = await ReadAllFromJSON("menu/adminlist_report.json")

    first_student_id = list(studentsData.keys())[0]
    first_student_name = studentsData[first_student_id]["name"]

    # 判斷若 contents 為空或 contents 第一個按鈕的 label 與第一位學生的名字不同
    if len(datas["body"]["contents"]) == 0 or first_student_name not in datas["body"]["contents"][0]["contents"][0]["action"]["label"]:
        datas["body"]["contents"] = await GetContentsFromStudents('setadmin')
        await WriteToJSON("menu/adminlist_report.json", "body", datas["body"])

        cprint("將 students 資料加入 adminList 完成", "green", "on_dark_grey")


# ----------------------------------------------------
# 設定管理員
# uid: 用戶的 UID
# token: 用戶的回覆令牌
# ----------------------------------------------------
async def Set_Admin(uid, admin_uid):
    try:
        from api.line_api import LineAPI

        if(uid == ''):
            return "請先設定UID"

        if uid in admin_uid:
            return f"{uid}已經是管理員了"

        data = await ReadFromJSONwithUID("students_data.json",f'{uid}')
        if data == None:
            return "請先設定UID"
    
        data['isAdmin'] = True
        await WriteToJSONwithUID("students_data.json",f'{uid}',data)
    
        # 切換至管理員 rich menu
        menu_ids = await ReadAllFromJSON("rich_menu_ids.json")
        await LineAPI().LinkRichMenuToUser(uid, menu_ids["admin"])

        cprint(f'{uid} 設定為管理員成功', "green", "on_dark_grey")
    
        return f'{uid}設定為管理員成功'

    except Exception as e:
        cprint(e, "red")
        return "設定管理員發生錯誤"


# ----------------------------------------------------
# 設定 UID
# content: 用戶的回覆內容
# uid: 用戶的 UID
# token: 用戶的回覆令牌
# ----------------------------------------------------
async def Set_Uid(content, uid, admin_uid):
       try:
            # 從回覆內容中獲取 ID
            prompts = content.split('-')
            id = prompts[0]
            data = await ReadFromJSON("students_data.json",f'{id}')
        
            data['uid'] = f'{uid}'
            await WriteToJSON("students_data.json",f'{id}',data)
            cprint(f'{id} 設定 uid {uid} succeed', "green", "on_dark_grey")
            
            if len(admin_uid) == 0:
                textMsg = TextMessage(text=f'{id}設定UID成功，\n目前管理員為空，\n請點擊下方按鈕成為管理員')
                menu = await GetFlexMessage('init_admin' ,'report')
                messages = [textMsg, menu]

                return messages

            return TextMessage(text=f'{id}設定UID成功')

       except Exception as e:
            cprint(e, "red")
            return TextMessage(text="設定UID發生錯誤")
       

# ----------------------------------------------------
# 獲取 FlexMessage
# menuName: 菜單名稱
# menuType: 菜單類型（output 輸出、report 回報）
# ----------------------------------------------------
async def GetFlexMessage(menuName = '' ,menuType = 'output'):
    fileName = f'menu/{menuName}list_{menuType}.json'
    menu = await ReadAllFromJSON(fileName)
    alt = menu['header']['contents'][0]['text']
    menu_json_str = json.dumps(menu)
    menu_message = FlexMessage(alt_text=alt,contents=FlexContainer.from_json(menu_json_str))

    return menu_message


# ----------------------------------------------------
# 回傳已設定的 UID 列表
# token: 用戶的回覆令牌
# ----------------------------------------------------
async def Output_Uid():
       try:
            datas = await ReadAllFromJSON("students_data.json")
            list = '已設定 UID 列表：\n'
            
            for key in datas.keys():
                uid = datas[f'{key}']['uid']
                if uid == '':
                    continue
                
                list += f'{key}：{uid}\n'
        
            return list
           
       except Exception as e:
            cprint(e, "red")
            return "獲取UID列表發生錯誤"


# ----------------------------------------------------
# 為指定的 UID 設定其回報的內容
# event: LINE 事件
# uid: 用戶的 UID
# dataName: 要設定的回報類型
# content: 回報內容
# ----------------------------------------------------
async def Set_data(uid ,dataName ,content):
       try:
            content = content.split('\n')
                
            if len(content) >2:
                    return "格式錯誤，請確認格式後再回報。"
                    
            id = ''
            isSetUid = False
            datas = await ReadAllFromJSON("students_data.json")
            
            for key in datas.keys():
                if datas[f'{key}']['uid'] == uid:
                    id = key
                    data = datas[f'{key}']
                    data[f'{dataName}'] = f'{content[1]}'
            
                    await WriteToJSON("students_data.json",f'{key}',data)
                    
                    isSetUid = True
                    
            if not isSetUid:
                return f'請先設定UID後再回報。'
            
            else:
                cprint(f'新增 {dataName} 成功', "green", "on_dark_grey")
                return f'{id} 新增回報成功'
           
       except Exception as e:
            cprint(e, "red")
            return "回報發生錯誤"


# ----------------------------------------------------
# 回傳 尚未回報的人員 給使用者
# dataName: 要回報的類型
# alt: 回報的標題
# ----------------------------------------------------
async def Get_Nonreport(dataName ,alt):
       try:
            nonReport_list = ''
            amount = 0
            datas= await ReadAllFromJSON('students_data.json')
            
            for key in datas.keys():
                if datas[f'{key}'][f'{dataName}'] == '':
                    name = datas[f'{key}']['name']
                    nonReport_list = nonReport_list + f'@{name}  '
                    amount += 1
            
            cprint(f'取得尚未回報人員資料成功', "green", "on_dark_grey")
        
            return f'{alt}尚未回報人員：\n{nonReport_list}\n共{amount}員'
           
       except Exception as e:
            cprint(e, "red")
            return "獲取資料發生錯誤"
           

# ----------------------------------------------------
# 回傳 統計回報內容 給使用者
# event: LINE 事件
# dataName: 要統計的回報類型
# alt: 統計回報的標題
# ----------------------------------------------------
async def Get_Totalreport(dataName ,alt):
       try:
            classData = await ReadAllFromJSON("class_data.json")
            class_name = classData['className']
            class_number = classData['classNumber']

            if class_number == '' or class_name == '':
                return "請先設定班級"

            totalReport_list = ''
            datas= await ReadAllFromJSON('students_data.json')
            
            for key in datas.keys():
                data = datas[f'{key}'][f'{dataName}']
                name = datas[f'{key}']['name']
                if data == '':
                    data = f'{key} {name}：尚未回報'
                
                totalReport_list = totalReport_list + f'{class_number}-{data}\n'
                
            
            cprint(f'取得統計回報資料成功', "green", "on_dark_grey")
        
            return f'{class_name} {alt}\n{totalReport_list}'
           
       except Exception as e:
            cprint(e, "red")
            return "獲取資料發生錯誤"


# ----------------------------------------------------
# 回傳 專車回報內容 給使用者
# 具有簡單的錯字檢查功能，需依照實際需求進行調整
# event: LINE 事件
# content: 專車回報內容
# ----------------------------------------------------
async def BusReportAnalysis(event ,content):    
    upStation_amount = {}
    downStation_amount = {}
    detectWords = False
    
    lines = content.split('\n')
    for line in lines:
        
        # 判斷是否包含錯誤的站名
        # 需依照實際需求進行調整
        if '左營' in line or '新左營' in line or '仿寮' in line:
            detectWords = True
            
        line = line.replace('(' ,'（').replace(')' ,'）').replace(' ' ,'').replace('左營' ,'高鐵').replace('新左營' ,'高鐵').replace('仿寮' ,'枋寮')
        
        # 判斷是否包含正確的括號
        if '（' not in line:
            continue
        
        # 取得上下車的車站名稱
        upStation = line.split('（')[1].split('）')[0]
        downStation = line.split('（')[2].split('）')[0]
        
        if upStation == '' or downStation == '':
            continue
        
        if upStation in upStation_amount:
            upStation_amount[f'{upStation}'] += 1
        else:
            upStation_amount[f'{upStation}'] = 1
            
        if downStation in downStation_amount:
            downStation_amount[f'{downStation}'] += 1
        else:
            downStation_amount[f'{downStation}'] = 1
     
    total = '放假數量統計\n'
    for station in upStation_amount.keys():
        amount = upStation_amount[f'{station}']
        total = total + f'{station} {amount}\n'
        
    total = total + '\n收假數量統計\n'
    for station in downStation_amount.keys():
        amount = downStation_amount[f'{station}']
        total = total + f'{station} {amount}\n'
        
    if detectWords :
        total = total + '\n偵測到錯誤站名，已自動更正'
    
    cprint(f'取得專車回報資料成功', "green", "on_dark_grey")
    
    return total