import telebot
from telebot import types
import websocket
import ssl
import json
import gzip
import random
import threading
import time

# --- إعدادات VIP ---
TOKEN = '8296272277:AAEDBA0CIAcWxUxcNm0CpBoeYZ3_AIS5sJM'
ADMIN_ID = 8233835640  # ضع الآيدي الخاص بك هنا
bot = telebot.TeleBot(TOKEN)

# متغيرات النظام
stats = {"created": 0, "failed": 0, "running": False}

def generate_user():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

def create_logic(chat_id, count):
    global stats
    stats["running"] = True
    
    for i in range(count):
        if not stats["running"]: break
        
        user = generate_user()
        # هنا تضع الـ Payload الكامل الخاص بك (تم اختصاره للعرض)
        payload = {"action": "Register", "login": user, "id": str(int(time.time()))}
        
        try:
            ws = websocket.create_connection("wss://193.200.173.45/Auth", sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=10)
            ws.send(json.dumps(payload))
            res = ws.recv()
            ws.close()
            
            stats["created"] += 1
            bot.send_message(chat_id, f"💎 **حساب VIP جديد**\n━━━━━━━━\n👤 يوزر: `{user}`\n🔑 رمز: `hhhh`", parse_mode="Markdown")
        except:
            stats["failed"] += 1
            
    stats["running"] = False
    bot.send_message(chat_id, "🏁 **اكتملت المهمة بنجاح!**", reply_markup=main_menu())

# --- لوحة التحكم (UI) ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🚀 بدء العمل", callback_data="start_work"),
        types.InlineKeyboardButton("🛑 إيقاف", callback_data="stop_work"),
        types.InlineKeyboardButton("📊 الإحصائيات", callback_data="show_stats"),
        types.InlineKeyboardButton("🔄 تصفير", callback_data="reset_stats")
    )
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_message(message.chat.id, "🔥 **أهلاً بك في لوحة تحكم DEALER OF DEATH VIP**\n\nإدارة الإنشاء التلقائي بين يديك الآن.", reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "start_work":
        msg = bot.send_message(call.message.chat.id, "🔢 كم عدد الحسابات المطلوب إنشاؤها؟")
        bot.register_next_step_handler(msg, process_count)
    elif call.data == "stop_work":
        stats["running"] = False
        bot.answer_callback_query(call.id, "🛑 تم طلب الإيقاف...")
    elif call.data == "show_stats":
        txt = f"📈 **إحصائيات العمل:**\n\n✅ ناجح: {stats['created']}\n❌ فشل: {stats['failed']}\n⚡ الحالة: {'يعمل' if stats['running'] else 'متوقف'}"
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode="Markdown")
    elif call.data == "reset_stats":
        stats["created"] = 0
        stats["failed"] = 0
        bot.answer_callback_query(call.id, "🔄 تم التصفير")

def process_count(message):
    try:
        count = int(message.text)
        threading.Thread(target=create_logic, args=(message.chat.id, count)).start()
        bot.send_message(message.chat.id, f"⚙️ جاري بدء عملية إنشاء {count} حساب...")
    except:
        bot.send_message(message.chat.id, "❌ يرجى إرسال رقم صحيح.")

bot.infinity_polling()
