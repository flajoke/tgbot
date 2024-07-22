from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler

# Константы
TOKEN: Final = ''
BOT_USERNAME: Final = '@nstu_works_bot'

# Команды
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("1 курс", callback_data='kurs_1'),
            InlineKeyboardButton("2 курс", callback_data='kurs_2'),
            InlineKeyboardButton("3 курс", callback_data='kurs_3'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите курс:', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Если Вы хотите купить какую-то работу на заказ, либо же хотите задать какие-то вопросы - тут надо бы чото придумать чтобы конф соблюдать ыы')

async def sosi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response_text = "Информация на команду /sosi"
    await update.message.reply_text(response_text)

# Обработчики сообщений
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

# Обработчики кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data.startswith('kurs_'):
        # Сохраняем выбранный курс
        course_keyboards[user_id] = data

    if data.startswith('back_to_'):
        if data == 'back_to_kurs':
            message_text = "Выберите курс:"
            keyboard = [
                [
                    InlineKeyboardButton("1 курс", callback_data='kurs_1'),
                    InlineKeyboardButton("2 курс", callback_data='kurs_2'),
                    InlineKeyboardButton("3 курс", callback_data='kurs_3'),
                ]
            ]
        else:
            # Используем сохраненный курс при возврате
            kurs = course_keyboards.get(user_id, 'kurs_1')  # По умолчанию 'kurs_1'
            message_text = "Выберите семестр:"
            keyboard = course_keyboards.get(kurs, [])
            keyboard = keyboard.copy()  # Создаем копию списка кнопок
            keyboard.append(back_button('back_to_kurs'))

    else:
        # Обработка остальных callback data
        if data in course_keyboards:
            message_text = "Выберите семестр:"
            keyboard = course_keyboards[data].copy()  # Создаем копию списка кнопок
            keyboard.append(back_button('back_to_kurs'))

        elif data.startswith('sem_'):
            await select_subject(update, context, data)
            return  # Выход, так как select_subject сам обрабатывает сообщение

        elif data.startswith('subject_'):
            parts = data.split('_')
            selected_semester = '_'.join(parts[1:-1])
            subject_num = parts[-1]
            await select_work_type(update, context, selected_semester, subject_num)
            return  # Выход, так как select_work_type сам обрабатывает сообщение

        elif data.startswith('worktype_'):
            _, subject_num, work_type = data.split('_', 2)
            work_type = work_type.replace('_', ' ')
            message_text = f"Вы выбрали {work_type} для предмета {subject_num}"
            keyboard = []  # Здесь может быть логика для следующего шага или пустая клавиатура

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message_text, reply_markup=reply_markup)


def back_button(callback_data):
    return [InlineKeyboardButton("Назад", callback_data=callback_data)]

# Утилиты
async def select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_semester: str):
    subjects = subjects_by_semester.get(selected_semester, [])
    # Создаем новый список кнопок
    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"subject_{selected_semester}_{subject.replace(' ', '_')}") for subject in subjects]
    ]

    # Добавляем кнопку "Назад" для возвращения к выбору семестра
    kurs = selected_semester.split('_')[1]  # Получаем номер курса из selected_semester
    keyboard.append(back_button(f'back_to_sem_{kurs}'))

    message_text = semester_messages.get(selected_semester, "Выберите предмет:")
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.edit_message_text(text=message_text, reply_markup=reply_markup)

async def select_work_type(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_semester: str, subject_num: str):
    work_types = work_types_by_semester_and_subject.get(selected_semester, {}).get(subject_num, ["Нет доступных работ"])
    # Создаем новый список кнопок
    keyboard = [
        [InlineKeyboardButton(work_type, callback_data=f"worktype_{subject_num}_{work_type.replace(' ', '_')}") for work_type in work_types]
    ]

    # Добавляем кнопку "Назад" для возвращения к выбору предмета
    kurs = selected_semester.split('_')[1]  # Получаем номер курса из selected_semester
    keyboard.append(back_button(f'back_to_subject_{selected_semester}_{kurs}'))

    message_text = f"Выберите тип работы для предмета:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.edit_message_text(text=message_text, reply_markup=reply_markup)

# Словари
course_keyboards = {
    'kurs_1': [
        [InlineKeyboardButton("Первый семестр", callback_data='sem_1')],
        [InlineKeyboardButton("Второй семестр", callback_data='sem_2')]
    ],
    'kurs_2': [
        [InlineKeyboardButton("Третий семестр", callback_data='sem_3')],
        [InlineKeyboardButton("Четвертый семестр", callback_data='sem_4')]
    ],
    'kurs_3': [
        [InlineKeyboardButton("Пятый семестр", callback_data='sem_5')]
        # Здесь можно добавить шестой семестр при необходимости
    ]
    # Добавьте другие курсы при необходимости
}

subjects_by_semester = {
    'sem_1': ["1", "2", "3", "4"],
    'sem_2': ["1", "2", "3", "4", "5"],
    'sem_3': ["1", "2", "3", "4"],
    'sem_4': ["1", "2", "3", "4", "5", "6", "7"],
    'sem_5': ["1", "2", "3", "4", "5", "6", "7", "8"]
    # Добавьте другие семестры при необходимости
}

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

back_button_data = {
    'sem': 'back_to_kurs',
    'subject': 'back_to_sem',
    'worktype': 'back_to_subject'
}

# Основная часть
if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    print('Started.')

    # Регистрация обработчиков
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('sosi', sosi_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error)

    # Запуск бота
    app.run_polling()
