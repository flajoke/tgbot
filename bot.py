from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

TOKEN: Final = '6711292079:AAGob9yiKuepK88G31X8KDdCBTR3Suh-uJo'
BOT_USERNAME: Final = '@nstu_works_bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1 курс", callback_data='folder_1'),
            InlineKeyboardButton("2 курс", callback_data='folder_2'),
            InlineKeyboardButton("3 курс", callback_data='folder_3')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите папку:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'folder_1':
        keyboard = [
            [InlineKeyboardButton("предмет фамилия 1", callback_data='subfolder_1_1')],
            [InlineKeyboardButton("предмет фамилия 2", callback_data='subfolder_1_2')],
            # ... добавьте столько подкатегорий, сколько вам нужно
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выбрана Папка 1. Выберите подкатегорию:", reply_markup=reply_markup)
    elif data == 'folder_2':
        keyboard = [
            [InlineKeyboardButton("предмет фамилия 1", callback_data='subfolder_2_1')],
            [InlineKeyboardButton("предмет фамилия 2", callback_data='subfolder_2_2')],
            # ... добавьте столько подкатегорий, сколько вам нужно
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выбрана Папка 2. Выберите подкатегорию:", reply_markup=reply_markup)
    elif data == 'folder_3':
        keyboard = [
            [InlineKeyboardButton("предмет фамилия 1", callback_data='subfolder_3_1')],
            [InlineKeyboardButton("предмет фамилия 2", callback_data='subfolder_3_2')],
            # ... добавьте столько подкатегорий, сколько вам нужно
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выбрана Папка 3. Выберите подкатегорию:", reply_markup=reply_markup)
    # Обработка выбора подкатегорий
    elif data.startswith('subfolder_'):
        # Здесь логика для обработки выбора подкатегории
        await query.edit_message_text(text=f"Выбрана {data}")
        # Вы можете добавить здесь дополнительную логику для каждой подкатегории


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('smth about our contacts')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{type}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)
    
    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()


    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Message ?
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))  # исправлено тут, добавлено условие для фильтрации команд

    # Callback query handler for inline keyboard buttons
    app.add_handler(CallbackQueryHandler(button))

    # Errors
    app.add_error_handler(error)

    # Polls the bot ?
    app.run_polling(poll_interval = 1)