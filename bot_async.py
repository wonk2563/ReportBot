import uvicorn
from api.line_api import LineAPI
import handlers.datahandler as datahandler
import handlers.eventhandler as eventhandler
import handlers.jobhandler as jobhandler
from fastapi import Request, FastAPI, HTTPException
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from termcolor import cprint


app = FastAPI()
scheduler = None

@app.on_event('startup')
async def init():

    cprint('機器人啟動中...', "green", "on_dark_grey")

    global scheduler
    scheduler = jobhandler.Init_job()
    print(scheduler)

    # 為所有用戶連接 rich menu
    await LineAPI().LinkRichMenuToAllUser()

    # 創建 uidlist_report.json
    await datahandler.CreateIdListFile()

    # 創建 adminlist_report.json
    await datahandler.CreateAdminIdListFile()


@app.post('/callback')
async def handle_callback(request: Request):
    cprint('接收 LINE 訊息...', "light_grey", "on_dark_grey")

    # 取得 LINE 的簽章驗證
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    body = body.decode()
    
    # 驗證訊息簽章
    try:
        events = LineAPI().parser.parse(body, signature)
        
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        await eventhandler.handle_event(event)
             
    return 'OK'

    
    
if __name__ == "__main__":
    
    # 啟動 FastAPI 應用程式
    uvicorn.run(
        "bot_async:app",
        host="0.0.0.0",
        port=5000,
        workers=4,
        log_level="info",
        access_log=True,
        use_colors=True,
        reload=True,
    )