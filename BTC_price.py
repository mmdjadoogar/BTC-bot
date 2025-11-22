from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
import requests
import sqlite3
import datetime


my_db = sqlite3.connect("BTC_price.db")
cur = my_db.cursor()
cur.execute('create table if not exists daily_price (id INTEGER PRIMARY KEY AUTOINCREMENT, price INTEGER, sign VARCHAR, date INTEGER)')

BTC_TOKEN = "8101818593:AAG7IUaZsTKW-WlZHPI38n4WSIBVZXBTPIY"
app = ApplicationBuilder().token(BTC_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.bot.send_message(chat_id=update.effective_user.id, text="سلام! به ربات قیمت بیت‌کوین خوش آمدید.")
    
    context.job_queue.run_repeating(
        callback=set_daly_price,
        interval=86400,
        first=0,
        chat_id=update.effective_user.id
    )
    await context.job_queue.start()
    
async def chekel(context):
    
    url = "https://apiv2.nobitex.ir/v3/orderbook/BTCIRT"

    response = requests.get(url)
    if 200 <= response.status_code < 300:
        
        data = response.json()
        last_week = last_week_price()
        price = list(data['lastTradePrice'])
        price.pop()
        price = int("".join(price))
        
        difference = int(data['lastTradePrice']) - int(last_week)
        difference = list(str(difference))
        difference.pop()

        difference = int("".join(difference))

        state = None
        
        if last_week < int(data['lastTradePrice']):
            state = "افزایش"
        elif last_week > int(data['lastTradePrice']):
            state = "کاهش"
        
        
        
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"""
قیمت لحظه ای بیتکوین: 
<b>{format(price, ',')}</b> تومان 💰
قیمت بیتکوین نسبت به هفته ی قبل  {format(difference, ',')} تومان {state} داشته است.
            """,
            parse_mode="HTML"
            )

    else:
        print("Failed to retrieve data from the API.")
    
async def chekel2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    url = "https://apiv2.nobitex.ir/v3/orderbook/BTCIRT"

    response = requests.get(url)
    
    if 200 <= response.status_code < 300:
        
        data = response.json()
        last_week = last_week_price()
        
        difference = int(data['lastTradePrice']) - last_week
        
        state = None
        
        if last_week < int(data['lastTradePrice']):
            state = "افزایش"
        elif last_week > int(data['lastTradePrice']):
            state = "کاهش"
        
        
        
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"""
قیمت لحظه ای بیتکوین: 
<b>{format(int(data['lastTradePrice']), ',')}</b> تومان 💰
قیمت بیتکوین نسبت به هفته ی قبل  {difference} تومان {state} داشته است.
            """,
            parse_mode="HTML"
            )

    else:
        print("Failed to retrieve data from the API.")
        
def chekel3():
    
    url = "https://apiv2.nobitex.ir/v3/orderbook/BTCIRT"

    response = requests.get(url)
    
    if 200 <= response.status_code < 300:
        data = response.json()
        
    return {
        "date" : data["lastUpdate"],
        "price" : data["lastTradePrice"]
        }
    
async def stop_repeating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.job_queue.stop()
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="تکرار متوقف شد.🚫"
    )
    print("Stopped repeating task.")

async def start_repeating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        del_time = context.args[0]
    except:
        pass

        
    if not context.args:
        return await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="لطفاً یک زمان معتبر وارد کنید.⚠️"
        )
    
    if del_time.endswith('s'):
        del_time = int(del_time.split('s')[0])
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"تایمر زمان شما به مدت {del_time} ثانیه تنظیم شد.")
        
    elif del_time.endswith('m'):
        del_time = int(del_time.split('m')[0]) * 60
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"تایمر زمان شما به مدت {del_time}دقیقه تنظیم شد.")
        
    elif del_time.endswith('h'):
        del_time = int(del_time.split('h')[0]) * 3600  
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"تایمر زمان شما به مدت {del_time} ساعت تنظیم شد.")
    
        
    
    context.job_queue.run_repeating(
        callback=chekel,
        interval=del_time,
        first=0,
        chat_id=update.effective_user.id
    )
    await context.job_queue.start()

async def set_daly_price(context):
    sign = "BTCIR"
    information = chekel3()
    query = 'INSERT INTO daily_price (price, sign, date) VALUES (?, ?, ?)'
    cur.execute(query, (information["price"], sign, information["date"]))    
    my_db.commit()

def extract_hms(unix_time):
    dt = datetime.datetime.fromtimestamp(unix_time)
    return dt.day, dt.hour, dt.minute, dt.second

def last_week_price():
    query = "SELECT * FROM daily_price ORDER BY date DESC"
    data = cur.execute(query).fetchall()
    return data[6][1]
    






async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return print(f'error : {context.error}')

if __name__ == "__main__":
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", chekel2))
    app.add_handler(CommandHandler("stop", stop_repeating))
    app.add_handler(CommandHandler("time", start_repeating))
    app.add_error_handler(error_handler)
    
    print("Bot is running...")
    app.run_polling()