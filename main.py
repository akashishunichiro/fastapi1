import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import asyncio

# --- SOZLAMALAR ---
BOT_TOKEN = "8535047554:AAHumC1Zd6f4xRqjH07nVGZnAvI4J1JaVUI"  # Tokeningizni qo'ying
ADMIN_CHAT_ID = 5820630707 # Admin chat ID si

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Foydalanuvchi holatlari
user_states = {}  # {chat_id: 'waiting_template'}


# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Salomlashish
    welcome_text = (
        f"👋 Assalomu alaykum, {user.first_name}!\n\n"
        f"📚 <b>Multi-Level Record</b> rasmiy botiga xush kelibsiz.\n"
        f"Quyidagi tugma orqali ma'lumotlarni yuborishingiz mumkin."
    )

    # Inline tugma
    keyboard = [[InlineKeyboardButton("📝 Savollarni yuborish", callback_data="send_questions")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

    # Holatni tozalash
    if chat_id in user_states:
        del user_states[chat_id]


# Inline tugma bosilganda
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    if query.data == "send_questions":
        # Shablonni yuborish
        template_text = (
            "📋 <b>Iltimos quyidagi ma'lumotlarni to'ldiring:</b>\n\n"
            "1️⃣ <b>Candidate name:</b>\n"
            "(Ism va familiyangizni yozing)\n\n"
            "2️⃣ <b>Exam date:</b>\n"
            "(Imtixon sanasi, masalan: 25.06.2025)\n\n"
            "3️⃣ <b>City/Region:</b>\n"
            "(Shahar va tumaningiz)\n\n"
            "4️⃣ <b>Speaking Part 1.1:</b>\n"
            "(Savolga javob)\n\n"
            "5️⃣ <b>Speaking Part 1.2:</b>\n"
            "(Rasmlarda nima borligini o'zbekcha yozing)\n\n"
            "6️⃣ <b>Speaking Part 2:</b>\n"
            "(2-qism javobi)\n\n"
            "7️⃣ <b>Speaking Part 3:</b>\n"
            "(3-qism javobi)\n\n"
            "📝 <i>Javoblaringizni yuqoridagi ketma-ketlikda yuboring:</i>"
        )

        await query.message.reply_text(template_text, parse_mode='HTML')

        # Holatni o'zgartirish: shablon kutilmoqda
        user_states[chat_id] = 'waiting_template'

        # Qo'shimcha: namuna uchun
        example_text = "🔍 <b>Misol:</b>\n\nAlijon Valiyev\n25.06.2025\nToshkent, Yunusobod\nMen ertalab turaman...\nRasmda kitob va qalam bor...\nMen sevgan mashg'ulot...\nKelajak rejalarim..."
        await query.message.reply_text(example_text, parse_mode='HTML')


# Foydalanuvchi xabarlarini qabul qilish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text
    user = update.effective_user

    # Holatni tekshirish
    current_state = user_states.get(chat_id)

    if current_state == 'waiting_template':
        # Shablon ma'lumotlari qabul qilindi
        await process_template(update, context, user_message)
    else:
        # Oddiy xabar
        await update.message.reply_text(
            "Iltimos, avval /start ni bosing va tugma orqali ma'lumotlarni yuboring."
        )


# Shablonni qayta ishlash
async def process_template(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
    chat_id = update.effective_chat.id
    user = update.effective_user

    # Ma'lumotlarni qatorlarga ajratish
    lines = message_text.strip().split('\n')

    # Ma'lumotlarni tartiblash
    try:
        # Kamida 7 qator bo'lishi kerak
        if len(lines) >= 7:
            candidate_name = lines[0].strip()
            exam_date = lines[1].strip()
            city_region = lines[2].strip()
            speaking11 = lines[3].strip()
            speaking12 = lines[4].strip()
            speaking2 = lines[5].strip()
            speaking3 = '\n'.join(lines[6:]).strip()  # Qolgan hammasi speaking3
        else:
            # Agar qatorlar kam bo'lsa, hammasini bitta qilib yuboramiz
            await update.message.reply_text(
                "❌ Ma'lumotlar yetarli emas. Iltimos, barcha 7 qismni to'liq yozing.\n"
                "Yoki /start ni bosib qaytadan urinib ko'ring."
            )
            return
    except Exception as e:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, ma'lumotlarni to'g'ri formatda yuboring."
        )
        logger.error(f"Xatolik: {e}")
        return

    # Foydalanuvchiga tasdiq
    await update.message.reply_text(
        "✅ Ma'lumotlaringiz qabul qilindi va adminga yuborildi.\n"
        "Tez orada javob olasiz!"
    )

    # Adminga xabar tayyorlash
    admin_message = (
        f"📬 <b>YANGI MA'LUMOTLAR</b>\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user.full_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📅 <b>Sana:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"━━━━━━━━━━━━━━━\n\n"
        f"<b>1. Candidate name:</b>\n{candidate_name}\n\n"
        f"<b>2. Exam date:</b>\n{exam_date}\n\n"
        f"<b>3. City/Region:</b>\n{city_region}\n\n"
        f"<b>4. Speaking Part 1.1:</b>\n{speaking11}\n\n"
        f"<b>5. Speaking Part 1.2:</b>\n{speaking12}\n\n"
        f"<b>6. Speaking Part 2:</b>\n{speaking2}\n\n"
        f"<b>7. Speaking Part 3:</b>\n{speaking3}\n\n"
        f"━━━━━━━━━━━━━━━"
    )

    # Adminga yuborish
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )
        logger.info(f"Admin ga yuborildi. User: {user.id}")
    except Exception as e:
        logger.error(f"Admin ga yuborishda xatolik: {e}")
        await update.message.reply_text(
            "⚠️ Ma'lumotlar qabul qilindi, lekin adminga yuborishda xatolik yuz berdi.\n"
            "Tez orada admin bilan bog'lanamiz."
        )

    # Holatni tozalash
    del user_states[chat_id]

    # Qayta start qilish uchun tugma
    keyboard = [[InlineKeyboardButton("🔄 Yangi ma'lumot yuborish", callback_data="send_questions")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Yana ma'lumot yuborish uchun quyidagi tugmani bosing:",
        reply_markup=reply_markup
    )


# Admin uchun maxsus komanda
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id == ADMIN_CHAT_ID:
        # Bot statistikasi
        active_users = len(user_states)
        await update.message.reply_text(
            f"📊 <b>Bot statistikasi</b>\n\n"
            f"👥 Faol foydalanuvchilar: {active_users}\n"
            f"🤖 Bot ishlamoqda ✅",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("Bu komanda faqat admin uchun!")


# Xatolarni qayta ishlash
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Xatolik yuz berdi: {context.error}")

    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Texnik xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring."
        )


def main():
    # Botni yaratish
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Xatolik handleri
    app.add_error_handler(error_handler)

    # Botni ishga tushirish
    print("🤖 Bot ishga tushdi...")
    print(f"Bot token: {BOT_TOKEN}")
    print(f"Admin ID: {ADMIN_CHAT_ID}")
    print("CTRL+C ni bosing to'xtatish uchun")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
