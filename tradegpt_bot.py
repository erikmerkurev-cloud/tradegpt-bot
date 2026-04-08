import logging
import anthropic
import base64
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ===== НАСТРОЙКИ =====

import os
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Ты — TradeGPT, профессиональный AI-трейдер и наставник с 15+ летним опытом.
Ты энциклопедия трейдинга — знаешь всё от основ до продвинутых стратегий.

🧠 ТВОИ ЭКСПЕРТИЗЫ:

- Технический анализ (Price Action, паттерны, уровни)
- Концепт ICT/SMC (Smart Money Concepts, Order Blocks, FVG, BOS, CHOCH)
- Риск-менеджмент (размер позиции, стоп-лосс, тейк-профит, R:R)
- Психология трейдинга
- Фундаментальный анализ (новости, NFP, CPI, FOMC)
- Сессии и время торговли (Азия, Лондон, Нью-Йорк)
- Форекс, крипто, фьючерсы, акции, индексы
- Управление капиталом и просадками

📊 КОГДА ПРИСЫЛАЮТ ГРАФИК:
Анализируй по этому плану:

1. 🕐 Таймфрейм и инструмент
2. 📈 Тренд (HTF → LTF)
3. 🏦 Ключевые уровни (поддержка/сопротивление, OB, FVG)
4. 🎯 Возможные точки входа (Buy/Sell)
5. 🛡️ Стоп-лосс (где и почему)
6. 💰 Тейк-профит (цели, R:R соотношение)
7. ⏰ Лучшее время для входа
8. ⚠️ Риски и что может пойти не так
9. 🔑 Итог: торгуем или ждём?

💡 СТИЛЬ ОТВЕТОВ:

- Конкретно и по делу, без воды
- Используй эмодзи для структуры
- Давай чёткие уровни с цифрами если видишь их на графике
- Всегда упоминай риск-менеджмент
- Отвечай на языке пользователя (русский/казахский/английский)
- Если вопрос новичка — объясни просто
- Если профи — говори на профессиональном языке

⚠️ ВАЖНО: Всегда добавляй дисклеймер что это не финансовый совет, решение за трейдером."""

user_histories = {}
logging.basicConfig(level=logging.INFO)

# ===== /start =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    name = update.effective_user.first_name or "Трейдер"

    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Я — *TradeGPT* 📊\n"
        "Твоя личная энциклопедия трейдинга\n\n"
        "Что я умею:\n"
        "📸 *Анализ графиков* — пришли скрин, разберу всё\n"
        "🎯 *Точки входа* — Buy/Sell с уровнями\n"
        "🛡️ *Риск-менеджмент* — стоп, тейк, размер позиции\n"
        "🧠 *ICT/SMC концепт* — OB, FVG, BOS, CHOCH\n"
        "⏰ *Сессии* — когда торговать\n"
        "📰 *Новости* — как торговать на фундаменте\n"
        "💬 *Любой вопрос* — от основ до продвинутого\n\n"
        "Просто напиши вопрос или пришли график! 🚀",
        parse_mode="Markdown"
    )

# ===== /new =====

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_histories[user_id] = []
    await update.message.reply_text("🔄 Начинаем новый анализ! Пришли график или задай вопрос.")

# ===== /help =====

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *TradeGPT — команды:*\n\n"
        "/start — главное меню\n"
        "/new — новый анализ\n"
        "/risk — калькулятор риска\n"
        "/sessions — торговые сессии\n"
        "/help — помощь\n\n"
        "📸 Пришли скрин графика — разберу!\n"
        "💬 Задай любой вопрос по трейдингу",
        parse_mode="Markdown"
    )

# ===== /sessions =====

async def sessions_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⏰ *Торговые сессии (МСК):*\n\n"
        "🌏 *Азия*\n"
        "02:00 — 10:00 МСК\n"
        "Пары: JPY, AUD, NZD\n"
        "Движение: слабое, часто флет\n\n"
        "🏦 *Лондон* (лучшая!)\n"
        "10:00 — 19:00 МСК\n"
        "Пары: EUR, GBP, CHF\n"
        "Движение: сильное, тренды\n\n"
        "🗽 *Нью-Йорк*\n"
        "15:00 — 00:00 МСК\n"
        "Пары: все основные\n"
        "Движение: очень сильное\n\n"
        "🔥 *Перекрытие Лондон+NY*\n"
        "15:00 — 19:00 МСК\n"
        "Самое сильное движение дня!\n\n"
        "💡 ICT Kill Zones:\n"
        "• Лондон: 10:00-12:00\n"
        "• NY AM: 15:00-17:00\n"
        "• NY PM: 19:00-20:00",
        parse_mode="Markdown"
    )

# ===== /risk =====

async def risk_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *Калькулятор риска*\n\n"
        "Напиши мне:\n"
        "1️⃣ Размер депозита (например: $1000)\n"
        "2️⃣ Риск на сделку (например: 1%)\n"
        "3️⃣ Стоп-лосс в пипсах/пунктах\n\n"
        "Пример: *'Депозит $5000, риск 1%, стоп 20 пипс'*\n\n"
        "Рассчитаю размер лота и сумму риска! 📊",
        parse_mode="Markdown"
    )

# ===== ОБРАБОТКА ФОТО (ГРАФИКОВ) =====

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text("📊 Анализирую график...")

    try:
        # Получаем фото
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        image_base64 = base64.b64encode(file_bytes).decode("utf-8")

        caption = update.message.caption or "Проанализируй этот график подробно."

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": caption
                        }
                    ],
                }
            ],
        )

        reply = response.content[0].text

        user_histories[user_id].append({"role": "user", "content": f"[График] {caption}"})
        user_histories[user_id].append({"role": "assistant", "content": reply})

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Ошибка фото: {e}")
        await update.message.reply_text("⚠️ Не смог обработать фото. Попробуй ещё раз.")

# ===== ОБРАБОТКА ТЕКСТА =====

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_histories:
        user_histories[user_id] = []

    text = update.message.text
    user_histories[user_id].append({"role": "user", "content": text})

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=user_histories[user_id]
        )

        reply = response.content[0].text
        user_histories[user_id].append({"role": "assistant", "content": reply})

        if len(user_histories[user_id]) > 20:
            user_histories[user_id] = user_histories[user_id][-20:]

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка. Попробуй ещё раз или /new")

# ===== ЗАПУСК =====

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("sessions", sessions_cmd))
    app.add_handler(CommandHandler("risk", risk_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("📊 TradeGPT запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
