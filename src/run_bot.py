import os
import random
from pathlib import Path
from dotenv import load_dotenv


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

token = os.getenv("TG_TOKEN")


stress_symb = "ёеуыаоэяию"
stress_symb += stress_symb.upper()

with Path.open(BASE_DIR / "words.txt", 'r', encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]


def get_random_word() -> str:
    return random.choice(lines)

async def get_user_markup(word:str, context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    words = []
    word_without_context = word.split("(")[0].strip()
    for i in range(len(word_without_context)):
        if word_without_context[i] in stress_symb:
            words.append(word_without_context[:i].lower() + word_without_context[i].upper() + word_without_context[i+1:].lower())

    keyboard = [
            [InlineKeyboardButton(i, callback_data=i)] for i in words
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["word"] = word_without_context

    return reply_markup


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    word = get_random_word()
    reply_markup = await get_user_markup(word, context)
    if context.user_data.get("4_task_complety_all", -1) == -1 and context.user_data.get("4_task_complety_correct", -1) == -1 and context.user_data.get("4_task_streak", -1) == -1:
        context.user_data["4_task_complety_correct"] = 0
        context.user_data["4_task_complety_all"] = 0
        context.user_data["4_task_streak"] = 0
        context.user_data["4_task_best_streak"] = 0
    await update.message.reply_text(f"Статистика:\nВсего решено: {context.user_data.get('4_task_complety_all', -1)}\nПравильно Решено: {context.user_data.get('4_task_complety_correct', -1)}\n Ваш стрик: {context.user_data.get('4_task_streak', -1)}\nЛучшая серия: {context.user_data.get('4_task_best_streak', -1)}\n\nСлово: {word.upper()}", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if context.user_data is None:
        return
    word = context.user_data.get("word", "")
    user_choice = query.data

    text = ""
    context.user_data["4_task_complety_all"] += 1
    if user_choice == word:
        text = f"✅ Правильно! {word}\n\n"
        context.user_data["4_task_complety_correct"] += 1
        context.user_data["4_task_streak"] += 1
    else:
        text = f"❌ Неверно, правильно: {word}\n\n"
        if context.user_data["4_task_streak"]  > context.user_data["4_task_best_streak"]:
            context.user_data["4_task_best_streak"] = context.user_data["4_task_streak"]
        context.user_data["4_task_streak"] = 0

    text += f"Статистика\nВсего решено {context.user_data.get('4_task_complety_all', -1)}\nПравильно решено: {context.user_data.get('4_task_complety_correct')}\nВаш стрик: {context.user_data.get('4_task_streak', -1)}\nЛучшая серия: {context.user_data.get('4_task_best_streak', -1)}\n\n"
    word = get_random_word()
    reply_markup = await get_user_markup(word, context)
    text += f"Слово: {word.upper()}\n"
    await query.edit_message_text(text=text, reply_markup=reply_markup)



app = ApplicationBuilder().token(token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

app.run_polling()




