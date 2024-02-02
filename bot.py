from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

TOKEN: Final = '6711292079:AAGob9yiKuepK88G31X8KDdCBTR3Suh-uJo'
BOT_USERNAME: Final = '@nstu_works_bot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1 курс", callback_data='kurs_1'),
            InlineKeyboardButton("2 курс", callback_data='kurs_2'),
            InlineKeyboardButton("3 курс", callback_data='kurs_3')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите папку:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'kurs_1':    
        keyboard = [
            [InlineKeyboardButton("Первый семестр", callback_data='sem_1')],
            [InlineKeyboardButton("Второй семестр", callback_data='sem_2')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите семестр:", reply_markup=reply_markup)
    elif data == 'kurs_2':
        keyboard = [
            [InlineKeyboardButton("Третий семестр", callback_data='sem_3')],
            [InlineKeyboardButton("Четвертый семестр", callback_data='sem_4')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите семестр:", reply_markup=reply_markup)
    elif data == 'kurs_3':
        keyboard = [
            [InlineKeyboardButton("Пятый семестр", callback_data='sem_5')],
            #[InlineKeyboardButton("Шестой семестр", callback_data='sem_6')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Выберите семестр:", reply_markup=reply_markup)
    # Обработка выбора подкатегорий
    elif data.startswith('sem_'):
        await select_subject(update, context, data)
    # Обработка выбора предмета
    elif data.startswith('subject_'):
        parts = data.split('_')
        selected_semester = '_'.join(parts[1:-1])
        subject_num = parts[-1]
        await select_work_type(update, context, selected_semester, subject_num)

    # Обработка выбора типа работы
    elif data.startswith('worktype_'):
        _, subject_num, work_type = data.split('_', 2)  # Изменено на разбиение на три части
        work_type = work_type.replace('_', ' ')
        await query.edit_message_text(text=f"Вы выбрали {work_type} для предмета {subject_num}")


semester_messages = {
    'sem_1': "Выберите предмет для первого семестра:\n1. Информатика (Балакин, Кондратьев, Романов)\n2. Мат. анализ (Филатов, Бутырин)\n3. Линейная алгебра (Судоплатов, Захаров)\n4. Учебная практика (Коршикова)",
    'sem_2': "Выберите предмет для второго семестра\n1. Программирование (Кондратьев, Балакин, Романов)\n2. Теория вероятности (Зыбарев, Пинигина, Симонов)\n3. Физика (Штыгашев)\n4. Дискретная математика (Судоплатов)\n5. Мат. анализ (Филатов, Бутырин)",
    'sem_3': "Выберите предмет для третьего семестра\n1. Программирование (Копылова)\n2. Компьютерная графика (Ильиных)\n3. Физика (Штыгашев)\n4. Электротехника (Заякин)",
    'sem_4': "Выберите предмет для четвертого семестра\n1. Вычислительная математика (Зыбарев, Борин)\n2. Информационные сети (Мищенко)\n3. Компьютерная графика (Дубков)\n4. Моделирование (Альсова)\n5. Операционные системы (Коршикова, Романов)\n6. Технологии и методы программирования (Копылова)\n7. Электроника (Шахтшнайдер)",
    'sem_5': "Выберите предмет для пятого семестра\n1. Архитектура средств вычислительной техники (Овчеренко)\n2. Базы данных (Трошина, Харюткина)\n3. Основы теории управления (Воевода)\n4. Информационные сети (Перышкова, Скороходов)\n5. Системный анализ (Гошко)\n6. Схемотехника (Гришанов)\n7. Учебная практика (Гошко)\n8. Параллельное программирование (Зеленчук, Малявко)",
    #'sem_6': "nothing now",
}

work_types_by_semester_and_subject = {
    'sem_1': {
        "1": ["Общая информация", "ЛР", "РГР"],
        "2": ["Общая информация", "Типовые расчеты"],
        "3": ["Общая информация", "Типовые расчеты"],
        "4": ["Общая информация", "Рефераты"],
    },
    'sem_2': {
        "1": ["Общая информация", "ЛР", "РГР"],
        "2": ["Общая информация", "ЛР", "РГР"],
        "3": ["Общая информация", "ЛР", "ИДЗ"],
        "4": ["Общая информация", "Типовые расчеты", "Практика"],
        "5": ["Общая информация", "Типовые расчеты"],
    },
    'sem_3': {
        "1": ["Общая информация", "ЛР", "Курсовые"],
        "2": ["Общая информация", "ЛР"],
        "3": ["Общая информация", "ЛР", "ИДЗ"],
        "3": ["Общая информация", "ИДЗ", "РГР"],
    },
    'sem_4': {
        "1": ["Общая информация", "ЛР", "РГР"],
        "2": ["Общая информация", "ЛР", "РГР"],
        "3": ["Общая информация", "ЛР", "РГР"],
        "4": ["Общая информация", "ЛР", "РГР"],
        "5": ["Общая информация", "ЛР", "РГР"],
        "6": ["Общая информация", "ЛР"],
        "7": ["Общая информация", "ЛР", "РГР"],
    },
    'sem_5': {
        "1": ["Общая информация", "ЛР", "РГР"],
        "2": ["Общая информация", "ЛР", "Курсовые"],
        "3": ["Общая информация", "ЛР", "РГР"],
        "4": ["Общая информация", "ЛР", "РГР"],
        "5": ["Общая информация", "РГР"],
        "6": ["Общая информация", "ЛР", "РГР"],
        "7": ["Общая информация", "Рефераты"],
        "8": ["Общая информация", "ЛР", "РГР"],
    },
    # Добавьте структуры для других семестров
}

async def select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_semester: str):
    if selected_semester == 'sem_1':
        subjects = ["1", "2", "3", "4"] 
    elif selected_semester == 'sem_2':
        subjects = ["1", "2", "3", "4", "5"] 
    elif selected_semester == 'sem_3':
        subjects = ["1", "2", "3", "4"] 
    elif selected_semester == 'sem_4':
        subjects = ["1", "2", "3", "4", "5", "6", "7"]    
    elif selected_semester == 'sem_5':
        subjects = ["1", "2", "3", "4", "5", "6", "7", "8"]    
    #elif selected_semester == 'sem_6':
        #subjects = ["я", "не ебу", "какие тут предметы"]    
    
    # Получаем индивидуальное сообщение для выбранного семестра
    message_text = semester_messages.get(selected_semester, "Выберите предмет:")

    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"subject_{selected_semester}_{subject.replace(' ', '_')}") for subject in subjects]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=message_text, reply_markup=reply_markup)

async def select_work_type(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_semester: str, subject_num: str):
    work_types = work_types_by_semester_and_subject.get(selected_semester, {}).get(subject_num, ["Нет доступных работ"])
    keyboard = [
        [InlineKeyboardButton(work_type, callback_data=f"worktype_{subject_num}_{work_type.replace(' ', '_')}") for work_type in work_types]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Выберите тип работы для предмета {subject_num} в {selected_semester}:", reply_markup=reply_markup)



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Если Вы хотите купить какую-то работу на заказ, либо же хотите задать какие-то вопросы - тут надо бы чото придумать чтобы конф соблюдать ыы')

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
    print('Started.')

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

    
