import os
from dotenv import load_dotenv
import telebot

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# دریافت توکن از متغیر محیطی
API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# حافظه موقتی کاربران
user_data = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "سلام! 👋\nبرای محاسبه لات لطفاً جفت‌ارز مورد نظر خود را وارد کنید (مثلاً: EUR/USD):")

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    chat_id = message.chat.id
    user_data.pop(chat_id, None)
    bot.send_message(chat_id, "🔄 داده‌ها پاک شدند. برای شروع دوباره /start را بزنید.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    # اگر کاربر هنوز با /start شروع نکرده
    if chat_id not in user_data:
        bot.send_message(chat_id, "برای شروع از /start استفاده کنید.")
        return

    user = user_data[chat_id]

    # مرحله ۱: دریافت جفت‌ارز
    if 'pair' not in user:
        user['pair'] = text
        bot.send_message(chat_id, "✅ حالا لطفاً مقدار سود یا ضرر هدف را به دلار وارد کنید (مثلاً 50):")

    # مرحله ۲: دریافت هدف دلاری
    elif 'target' not in user:
        try:
            user['target'] = float(text)
            bot.send_message(chat_id, "✅ حالا لطفاً فاصله پیپ را وارد کنید (مثلاً 20):")
        except ValueError:
            bot.send_message(chat_id, "❗ لطفاً یک عدد معتبر وارد کنید.")

    # مرحله ۳: دریافت پیپ و محاسبه
    elif 'pips' not in user:
        try:
            user['pips'] = float(text)
            pip_value = 10  # فرض مقدار هر پیپ برای یک لات کامل (مثلاً در EUR/USD)
            lot = user['target'] / (user['pips'] * pip_value)
            lot = round(lot, 3)

            msg = f"""✅ محاسبه انجام شد:

🔹 جفت‌ارز: {user['pair']}
💵 هدف: {user['target']} دلار
📏 فاصله پیپ: {user['pips']} پیپ

📊 مقدار لات مناسب: {lot} لات"""

            bot.send_message(chat_id, msg)
            user_data.pop(chat_id)
        except ValueError:
            bot.send_message(chat_id, "❗ لطفاً عدد معتبر وارد کنید.")

# اجرای دائمی ربات
bot.infinity_polling()
