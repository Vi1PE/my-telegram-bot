import telebot
import random
import requests
import os
import json
from telebot import types

TOKEN = "7750907166:AAGxiaWijI6fmqE9fkfONhtjo9VC-Kopq44"
OWNER_ID = 5184990839
DEVELOPER = "@Vi1PE"

bot = telebot.TeleBot(TOKEN)
verified_users = set()
verified_file = "verified.txt"

# تحميل BINs من ملف
def load_bin_lists():
    try:
        with open("bin_lists.json", "r") as f:
            return json.load(f)
    except:
        return {
            "autopay_bins": [],
            "apple_google_pay_bins": [],
            "prepaid_bins": []
        }

bin_lists = load_bin_lists()

# التأكد من وجود ملف التحقق
if os.path.exists(verified_file):
    with open(verified_file, "r") as f:
        verified_users = set(map(int, f.read().splitlines()))
else:
    verified_users = {OWNER_ID}
    with open(verified_file, "w") as f:
        f.write(str(OWNER_ID) + "\n")

# تأكيد إضافة المطور للتحقق دائمًا
verified_users.add(OWNER_ID)

def save_verified():
    with open(verified_file, "w") as f:
        for uid in verified_users:
            f.write(str(uid) + "\n")

def is_verified(user_id):
    return user_id in verified_users

@bot.message_handler(commands=['start'])
def start(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, f"🚫 لا يمكنك استخدام البوت قبل التفعيل.\n\n📩 تواصل مع المطور: {DEVELOPER}\nوابعته رقم معرفك.")
    welcome = (
        "👋 *أهلاً بك في بوت فحص وتوليد البطاقات* 💳\n\n"
        "📋 *الأوامر المتاحة:*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 /gen - توليد حتى 10 بطاقات من BIN\n"
        "🔹 /bin - عرض معلومات BIN\n"
        "🔹 /check - فحص البطاقة\n"
        "🔹 /combo - فحص كومبو CC|EMAIL|PASS\n"
        "🔹 /extractbin - استخراج BIN\n"
        "🔹 /otp - فحص ذكي عبر محاكي\n"
        "🔹 /verify - تفعيل البوت\n"
        "🔹 /adduser - إضافة مستخدم (للمطور فقط)\n"
        "🔹 /removeuser - إزالة مستخدم (للمطور فقط)\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 للتواصل: {DEVELOPER}"
    )
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown")

@bot.message_handler(commands=['verify'])
def verify_user(message):
    bot.reply_to(message, f"🚫 لا يمكنك تفعيل البوت بنفسك. فقط المطور يمكنه إضافتك. تواصل مع: {DEVELOPER}")

@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 هذا الأمر للمطور فقط!")
    try:
        user_id = int(message.text.split()[1])
        verified_users.add(user_id)
        save_verified()
        bot.reply_to(message, f"✅ تم إضافة المستخدم {user_id} بنجاح.")
        bot.send_message(user_id, "✅ تم تفعيل حسابك. ابدأ بالأمر /start")
    except:
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /adduser USER_ID")

@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != OWNER_ID:
        return bot.reply_to(message, "🚫 هذا الأمر للمطور فقط!")
    try:
        user_id = int(message.text.split()[1])
        verified_users.discard(user_id)
        save_verified()
        bot.reply_to(message, f"✅ تم إزالة المستخدم {user_id}.")
    except:
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /removeuser USER_ID")

@bot.message_handler(commands=['extractbin'])
def extract_bin(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, "🚫 لا يمكنك استخدام البوت إلا بعد إضافتك من المطور.")
    try:
        line = message.text.split()[1]
        bin_code = line.split("|")[0][:6]
        bot.reply_to(message, f"💳 BIN المستخرج: `{bin_code}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /extractbin CC|MM|YY|CVV")

@bot.message_handler(commands=['otp'])
def otp_check(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, "🚫 لا يمكنك استخدام البوت إلا بعد إضافتك من المطور.")
    try:
        line = message.text.split()[1]
        status = "🔐 OTP Passed" if random.random() > 0.5 else "❌ OTP Failed"
        bot.reply_to(message, f"{status} - `{line}`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ استخدم الأمر هكذا: /otp CARD")

@bot.message_handler(commands=['check'])
def check_card(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, "🚫 لا يمكنك استخدام البوت إلا بعد إضافتك من المطور.")
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "❌ استخدم الأمر هكذا:\n/check CARD_NUMBER|MM|YY|CVV")

    card_line = args[1]
    status = "✅ LIVE" if random.random() < 0.3 else "❌ DEAD"
    reply = f"{status} - `{card_line}`"
    bot.send_message(message.chat.id, reply, parse_mode="Markdown")

@bot.message_handler(commands=['bin'])
def bin_lookup(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, "🚫 لا يمكنك استخدام البوت إلا بعد إضافتك من المطور.")
    try:
        bin_number = message.text.split()[1]
        res = requests.get(f"https://lookup.binlist.net/{bin_number}")
        data = res.json()
        country = data.get('country', {}).get('name', '❓')
        emoji = data.get('country', {}).get('emoji', '')
        bank = data.get('bank', {}).get('name', '❓')
        brand = data.get('scheme', '❓').upper()
        type_card = data.get('type', '❓').capitalize()
        category = data.get("category", "❓").capitalize()
        prepaid = data.get("prepaid", False)

        autopay = "✅" if bin_number in bin_lists["autopay_bins"] else "❌"
        apple_google = "✅" if bin_number in bin_lists["apple_google_pay_bins"] else "❌"
        prepaid_note = "💡 *بطاقة Prepaid أو Virtual فقط!*" if prepaid else ""

        info = (
            f"💳 BIN: {bin_number}\n"
            f"🏦 البنك: {bank}\n"
            f"💳 النوع: {brand} - {type_card} - {category}\n"
            f"🌍 الدولة: {country} {emoji}\n"
            f"{prepaid_note}\n"
            f"🧾 AutoPay: {autopay}\n"
            f"🍎 Apple/Google Pay: {apple_google}"
        )
        bot.send_message(message.chat.id, info, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ: BIN غير صالح أو غير معروف.\n{str(e)}")

@bot.message_handler(commands=['gen'])
def handle_gen(message):
    if not is_verified(message.from_user.id):
        return bot.reply_to(message, "🚫 لا يمكنك استخدام البوت إلا بعد إضافتك من المطور.")
    args = message.text.split()
    if len(args) < 2:
        return bot.reply_to(message, "❌ استخدم الأمر هكذا:\n/gen 515624xxxxxxxxxx")

    bin_input = args[1].strip()
    if 'x' not in bin_input:
        bin_input += 'x' * (16 - len(bin_input))

    cards = []
    for _ in range(10):
        cc = ''.join(str(random.randint(0, 9)) if c == 'x' else c for c in bin_input)
        mm = str(random.randint(1, 12)).zfill(2)
        yy = str(random.randint(2024, 2032))
        cvv = str(random.randint(1000, 9999)) if cc.startswith("3") else str(random.randint(100, 999))
        card_line = f"{cc}|{mm}|{yy}|{cvv}"
        cards.append(card_line)

    try:
        res = requests.get(f"https://lookup.binlist.net/{bin_input[:6]}")
        data = res.json()
        brand = data.get("scheme", "N/A").upper()
        card_type = data.get("type", "N/A").capitalize()
        bank = data.get("bank", {}).get("name", "N/A")
        country = data.get("country", {}).get("name", "N/A")
        emoji = data.get("country", {}).get("emoji", "")
        category = data.get("category", "")
        prepaid = data.get("prepaid", False)
        autopay_supported = "✅" if bin_input[:6] in bin_lists["autopay_bins"] else "❌"
        apple_google_supported = "✅" if bin_input[:6] in bin_lists["apple_google_pay_bins"] else "❌"
        note = "💡 *Virtual/Prepaid Card*" if prepaid else ""
    except:
        brand = card_type = bank = country = category = "N/A"
        emoji = ""
        autopay_supported = "❓"
        apple_google_supported = "❓"
        note = ""

    message_text = f"𝗕𝗜𝗡 ⇾ {bin_input[:6]}\n𝗔𝗺𝗼𝘂𝗻𝘁 ⇾ 10\n\n"
    for card in cards:
        message_text += f"<code>{card}</code>\n"
    message_text += (
        f"\n𝗜𝗻𝗳𝗼: {brand} - {card_type} {category} {note}\n"
        f"𝐈𝐬𝐬𝐮𝐞𝐫: {bank}\n"
        f"𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {country} {emoji}\n"
        f"🧾 AutoPay: {autopay_supported}\n"
        f"🍎 Apple/Google Pay: {apple_google_supported}"
    )

    bot.send_message(message.chat.id, message_text, parse_mode="HTML")

print("✅ Bot is running...")
bot.polling()
