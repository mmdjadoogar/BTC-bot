from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
import requests

BTC_TOKEN = "8101818593:AAG7IUaZsTKW-WlZHPI38n4WSIBVZXBTPIY"
app = ApplicationBuilder().token(BTC_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.bot.send_message(chat_id=update.effective_user.id, text="سلام! به ربات قیمت بیت‌کوین خوش آمدید.")

async def chekel(context):
    
    url = "https://apiv2.nobitex.ir/v3/orderbook/BTCIRT"

    response = requests.get(url)
    if 200 <= response.status_code < 300:
        
        data = response.json()
        
        await context.bot.send_message(
            chat_id=context.job.chat_id,
            text=f"قیمت لحظه ای بیتکوین: <b>{data['lastTradePrice']}</b> 💰",
            parse_mode="HTML"
            )

    else:
        print("Failed to retrieve data from the API.")
    
async def chekel2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    url = "https://apiv2.nobitex.ir/v3/orderbook/BTCIRT"

    response = requests.get(url)
    if 200 <= response.status_code < 300:
        
        data = response.json()
        
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"قیمت لحظه ای بیتکوین: <b>{data['lastTradePrice']}</b> 💰",
            parse_mode="HTML"
            )

    else:
        print("Failed to retrieve data from the API.")

    
async def stop_repeating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.job_queue.stop()
    print("Stopped repeating task.")

async def start_repeating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    del_time = context.args[0]
    if del_time.endswith('s'):
        del_time = int(del_time.split('s')[0])
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"تایمر زمان شما به مدت {del_time} ثانیه تنظیم شد.")
        print(del_time)
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