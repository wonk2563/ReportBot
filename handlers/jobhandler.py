from apscheduler.schedulers.asyncio import AsyncIOScheduler
import handlers.datahandler as datahandler
from termcolor import cprint


_scheduler = None

def get_scheduler():
    global _scheduler
    return _scheduler
               
def Init_job():
    cprint('啟動調度器', "green", "on_dark_grey")
    global _scheduler
    _scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    
    # 休假回報（夜間回報）
    #星期一到日，中午十二點
    _scheduler.add_job(Set_nightDataEmpty, 'cron', day_of_week='0-6', hour=12, id = 'night')

    # 專車回報
    #每週四，晚上十一點
    _scheduler.add_job(Set_busDataEmpty, 'cron', day_of_week='4', hour=23, id ='bus')

    # 休假規劃
    #每週日，晚上十一點
    _scheduler.add_job(Set_vacationDataEmpty, 'cron', day_of_week='6', hour=23, id = 'vacation')

    # 收假回報
    #每週三，晚上十一點
    _scheduler.add_job(Set_closeDataEmpty, 'cron', day_of_week='2', hour=23, id = 'close')
    
    _scheduler.start()
    cprint('調度器執行中...', "yellow")

    return _scheduler

async def Del_data(dataName):
         datas = await datahandler.ReadAllFromJSON("data.json")
         for key in datas.keys():
             data = datas[f'{key}']
             data[f'{dataName}'] = ''
             
             await datahandler.WriteToJSON("data.json",f'{key}',data)
         cprint(f'成功刪除 {dataName} 資料', "green", "on_dark_grey")
         
async def Set_nightDataEmpty():
           cprint('開始刪除夜間回報資料', "green", "on_dark_grey")
           await Del_data('nightReport')
               
async def Set_busDataEmpty():
           cprint('開始刪除專車回報資料', "green", "on_dark_grey")
           await Del_data('busReport')
           
async def Set_vacationDataEmpty():
           cprint('開始刪除休假規劃資料', "green", "on_dark_grey")
           await Del_data('vacationReport')
           
async def Set_closeDataEmpty():
           cprint('開始刪除收假回報資料', "green", "on_dark_grey")
           await Del_data('closeReport')
    
async def Resume_job():
    scheduler = get_scheduler()
    scheduler.resume()
    cprint('調度器暫停', "green", "on_dark_grey")
    
async def Pause_job():
    scheduler = get_scheduler()
    scheduler.pause()
    cprint('調度器恢復工作', "green", "on_dark_grey")

async def Stop_job(jobName):
    scheduler = get_scheduler()
    scheduler.remove_job(jobName)
    cprint(f'已移除工作 {jobName}', "green", "on_dark_grey")
    
    
    