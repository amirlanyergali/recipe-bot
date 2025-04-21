from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
import random

TOKEN = "7598947295:AAGJ_PCn5OmWlHCKJZwCGnDmV6Rzv6tN0fk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🍗 Chicken", callback_data='Chicken'),
         InlineKeyboardButton("🥩 Beef", callback_data='Beef')],
        [InlineKeyboardButton("🍝 Pasta", callback_data='Pasta'),
         InlineKeyboardButton("🐟 Seafood", callback_data='Seafood')],
        [InlineKeyboardButton("🥬 Vegetarian", callback_data='Vegetarian'),
         InlineKeyboardButton("🍰 Dessert", callback_data='Dessert')],
        [InlineKeyboardButton("🎲 Random", callback_data='random')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👨‍🍳 *Welcome to Recipe Bot!*\n\nChoose a category below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍🍳 *Recipe Bot Instructions:*\n\n"
        "• Choose a category to get a recipe.\n"
        "• Click Random for a surprise dish.\n"
        "• Each recipe includes ingredients, instructions, and a link.\n\n"
        "приятного аппетита брат!",
        parse_mode="Markdown"
    )

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recipe = get_recipe("random")
    await update.message.reply_photo(photo=recipe["image"])
    await update.message.reply_text(recipe["text"], parse_mode="Markdown")

def get_ingredients(meal):
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}")
        mes = meal.get(f"strMeasure{i}")
        if ing and ing.strip():
            ingredients.append(f"• {ing.strip()} — {mes.strip()}")
    return "\n".join(ingredients)

def format_recipe(meal):
    title = meal.get("strMeal", "Recipe")
    img = meal.get("strMealThumb", "")
    instr = meal.get("strInstructions", "No instructions found.")
    ing = get_ingredients(meal)
    link = meal.get("strSource") or meal.get("strYoutube") or "No link available"

    text = f"*🍽 {title}*\n\n"
    text += f"*🥣 Ingredients:*\n{ing}\n\n"
    text += f"*📋 Instructions:*\n{instr[:1500]}{'...' if len(instr) > 1500 else ''}\n\n"
    text += f"🔗 [More details]({link})"
    return {"text": text, "image": img}

def get_recipe(choice=None):
    if choice != "random":
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={choice}"
        data = requests.get(url).json()
        meal = random.choice(data["meals"])
        meal_id = meal["idMeal"]
        full = requests.get(f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}").json()
        return format_recipe(full["meals"][0])
    else:
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        meal = requests.get(url).json()["meals"][0]
        return format_recipe(meal)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    recipe = get_recipe(choice)
    await query.message.reply_photo(photo=recipe["image"])
    await query.message.reply_text(recipe["text"], parse_mode="Markdown")

# 👇 ЭТО ДЛЯ REPLIT (без asyncio.run)
app = ApplicationBuilder().token(TOKEN).build()

# Добавляем команды в Telegram-меню
app.bot.set_my_commands([
    BotCommand("start", "🔄 Start the bot"),
    BotCommand("help", "ℹ️ Instructions"),
    BotCommand("random", "🎲 Get a random recipe")
])

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("random", random_command))
app.add_handler(CallbackQueryHandler(handle_buttons))

app.run_polling(allowed_updates=["message", "callback_query"])
