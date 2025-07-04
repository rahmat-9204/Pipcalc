import os
import threading
from dotenv import load_dotenv
import telebot
from flask import Flask

# بارگذاری توکن از .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# آی‌دی عددی مدیر ربات (از @userinfobot بگیر)
ADMIN_ID = 123456789  # ← این را با آیدی خودت جایگزین کن

# فایل ذخیره کاربران
USERS_FILE = "users.txt"

# حافظه موقتی کاربران
user_data = {}

# ذخیره کاربر جدید
def save_user(chat_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            pass
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(chat_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(str(chat_id) + "\n")

# پیام شروع
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    save_user(chat_id)
    user_data[chat_id] = {}
    bot.send_message(chat_id, "سلام! 👋\nبرای محاسبه لات لطفاً جفت‌ارز مورد نظر خود را وارد کنید (مثلاً: EUR/USD):")

# ریست
@bot.message_handler(commands=['reset'])
def handle_reset(message):
    chat_id = message.chat.id
    user_data.pop(chat_id, None)
    bot.send_message(chat_id, "🔄 داده‌ها پاک شدند. برای شروع دوباره /start را بزنید.")

# ارسال پیام به همه کاربران (فقط مدیر)
@bot.message_handler(commands=['post'])
def handle_post(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ فقط مدیر می‌تواند پیام عمومی ارسال کند.")
        return

    msg = message.text.split("/post", 1)[-1].strip()
    if not msg:
        bot.send_message(message.chat.id, "❗ لطفاً پیام را بعد از /post بنویس.")
        return

    success = 0
    fail = 0
    if not os.path.exists(USERS_FILE):
        bot.send_message(message.chat.id, "⚠️ هیچ کاربری ثبت نشده است.")
        return

    with open(USERS_FILE, "r") as f:
        user_ids = f.read().splitlines()

    for uid in user_ids:
        try:
            bot.send_message(int(uid), msg)
            success += 1
        except:
            fail += 1

    bot.send_message(message.chat.id, f"📢 پیام فرستاده شد.\n✅ موفق: {success}\n❌ ناموفق: {fail}")

# هندل اصلی پیام‌ها
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        bot.send_message(chat_id, "برای شروع از /start استفاده کنید.")
        return

    user = user_data[chat_id]

    if 'pair' not in user:
        user['pair'] = text
        bot.send_message(chat_id, "✅ حالا لطفاً مقدار سود یا ضرر هدف را به دلار وارد کنید (مثلاً 50):")

    elif 'target' not in user:
        try:
            user['target'] = float(text)
            bot.send_message(chat_id, "✅ حالا لطفاً فاصله پیپ را وارد کنید (مثلاً 20):")
        except ValueError:
            bot.send_message(chat_id, "❗ لطفاً یک عدد معتبر وارد کنید.")

    elif 'pips' not in user:
        try:
            user['pips'] = float(text)
            pip_value = 10
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

# اجرای ربات در یک ترد جداگانه
def run_bot():
    bot.infinity_polling()

# اجرای سرور Flask برای سازگاری با Render
@app.route('/')
def home():
    return "ربات آنلاین است ✅"

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
