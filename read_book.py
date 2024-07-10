import os
import random
import shutil
import json

import telebot


# Тимчасовий словник для зберігання імен файлів
temp_files = {}


# Функція для обробки вибору конкретної книги користувачем
def read_book(bot, message):
    search_criteria = message.text.lower().replace(' ', '_')
    sent_files = 0
    for filename in os.listdir('Books'):
        if search_criteria in filename.lower():
            new_filename = filename.replace('!!!', '!!')
            shutil.copy(os.path.join('Books', filename), os.path.join('Books', new_filename))
            with open(os.path.join('Books', new_filename), 'rb') as book_file:
                bot.send_document(message.chat.id, book_file)
                sent_files += 1
                # Зберігаємо ім'я файлу в тимчасовому словнику
                temp_files[message.chat.id] = filename
                # return # Якщо треба вертати першу потрапившу книгу
            os.remove(os.path.join('Books', new_filename))
    if sent_files == 0:
        bot.send_message(message.chat.id, 'На жаль, книгу за вашим запитом не знайдено')
    if sent_files == 1:
        # Додавання кнопки для додавання книги в список улюблених
        markup = telebot.types.InlineKeyboardMarkup()
        itembtn1 = telebot.types.InlineKeyboardButton('Так, додати', callback_data='add_favorite_book_after_read')
        itembtn2 = telebot.types.InlineKeyboardButton('Не треба', callback_data='cancel_add_favorite_book_after_read')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, 'Бажаєте додати цю книгу в список улюблених ?', reply_markup=markup)


def send_format_buttons(bot, chat_id):
    markup = telebot.types.InlineKeyboardMarkup()
    formats = ['PDF', 'FB2', 'EPUB', 'MOBI', 'AZW', 'AZW3', 'TXT']
    for i in range(0, len(formats), 2):
        # Створюємо дві кнопки для кожної пари форматів
        button1 = telebot.types.InlineKeyboardButton(formats[i], callback_data=f'read_book_random_{formats[i]}')
        row = [button1]
        # Якщо існує наступний формат, додаємо його до того ж рядка
        if i+1 < len(formats):
            button2 = telebot.types.InlineKeyboardButton(formats[i+1], callback_data=f'read_book_random_{formats[i+1]}')
            row.append(button2)
        markup.row(*row)
    sent_msg = bot.send_message(chat_id, 'Будь ласка, виберіть бажаний формат:', reply_markup=markup)
    return sent_msg.message_id


def send_random_book(bot, chat_id, format_msg_id, call):
    book_format = call.data.split('_')[-1]
    books_dir = 'Books'
    sent_files = 0
    books = [book for book in os.listdir(books_dir) if book.endswith(f'.{book_format.lower()}')]
    if books:
        random_book = random.choice(books)
        new_filename = random_book.replace('!!!', '!!')
        shutil.copy(os.path.join(books_dir, random_book), os.path.join(books_dir, new_filename))
        with open(os.path.join(books_dir, new_filename), 'rb') as book_file:
            bot.send_document(chat_id, book_file)
            sent_files += 1
        os.remove(os.path.join('Books', new_filename))  # remove the temporary file
    if sent_files == 0:
        bot.send_message(chat_id, f'На жаль, у бібліотеці поки немає книг у форматі {book_format}')
        send_format_buttons(bot, chat_id)
    bot.delete_message(chat_id=chat_id, message_id=format_msg_id)


def add_favorite_book(bot, user_id, chat_id, message):
    try:
        book_name = message.document.file_name
        book_name = book_name.replace('!!', '!!!')
        user_id = str(user_id)

        # Перевіряємо, чи існує такий файл у папці Books
        if book_name in os.listdir('Books'):
            # Перевіряємо, чи існує файл
            if not os.path.isfile('favorite_books.json'):
                # Якщо файл не існує, ініціалізуємо його порожнім словником
                with open('favorite_books.json', 'w') as f:
                    json.dump({}, f)
            
            # Завантажуємо поточний список улюблених книг
            with open('favorite_books.json', 'r') as f:
                if os.stat('favorite_books.json').st_size == 0:
                    favorite_books = {}
                else:
                    favorite_books = json.load(f)

            # Перевіряємо, чи книга вже є в списку
            if user_id in favorite_books and book_name in favorite_books[user_id]:
                bot.send_message(chat_id, 'Ця книга вже є в списку улюблених')
            else:
                # Додаємо нову книгу до списку
                if user_id in favorite_books:
                    favorite_books[user_id].append(book_name)
                else:
                    favorite_books[user_id] = [book_name]

            # Зберігаємо оновлений список у файл
            with open('favorite_books.json', 'w') as f:
                json.dump(favorite_books, f)
            bot.send_message(message.chat.id, f'Книга була успішно додана до Вашого списку улюблених!')
        else:
            msg1 = 'На жаль, дана книга не була знайдена в бібліотеці\n'
            msg2 = 'Будь ласка, переконайтеся, що Ви надіслали правильний файл'
            bot.send_message(message.chat.id, msg1 + msg2)
    except:
        bot.send_message(message.chat.id, f'Сталась помилка. \nПереконайтесь, що Ви надсилаєте файл книги')


def add_favorite_book_after_read(bot, user_id, chat_id):
    """
    Функція для додавання книги до списку улюблених
    """

    # Отримуємо ім'я файлу з тимчасового словника
    book_name = temp_files[chat_id]
    user_id = str(user_id)

    # Перевіряємо, чи існує файл
    if not os.path.isfile('favorite_books.json'):
        # Якщо файл не існує, ініціалізуємо його порожнім словником
        with open('favorite_books.json', 'w') as f:
            json.dump({}, f)
    
    # Завантажуємо поточний список улюблених книг
    with open('favorite_books.json', 'r') as f:
        if os.stat('favorite_books.json').st_size == 0:
            favorite_books = {}
        else:
            favorite_books = json.load(f)

    # Перевіряємо, чи книга вже є в списку
    if user_id in favorite_books and book_name in favorite_books[user_id]:
        bot.send_message(chat_id, 'Ця книга вже є в списку улюблених')
    else:
        # Додаємо нову книгу до списку
        if user_id in favorite_books:
            favorite_books[user_id].append(book_name)
        else:
            favorite_books[user_id] = [book_name]

    # Зберігаємо оновлений список у файл
    with open('favorite_books.json', 'w') as f:
        json.dump(favorite_books, f)
    
    # Видаляємо ім'я файлу з тимчасового словника
    del temp_files[chat_id]


def delete_favorite_book(bot, user_id, message):
    """
    Функція для видалення книги зі списку улюблених
    """
    try:
        # Отримуємо індекс книги з повідомлення користувача
        book_index = int(message.text) - 1
        user_id = str(user_id)
        
        # Завантажуємо поточний список улюблених книг
        with open('favorite_books.json', 'r') as f:
            favorite_books = json.load(f)

        # Видаляємо книгу зі списку
        if user_id in favorite_books:
            del favorite_books[user_id][book_index]

        # Зберігаємо оновлений список у файл
        with open('favorite_books.json', 'w') as f:
            json.dump(favorite_books, f)
        
        bot.send_message(user_id, 'Книгу успішно видалено зі списку улюблених')
    except:
        bot.send_message(user_id, 'Сталась помилка, спробуйте знову.\nПереконайтесь, що ви ввели номер книги зі списку')


def list_favorite_books(user_id):
    """
    Функція для отримання списку улюблених книг
    """
    try:
        # Завантажуємо поточний список улюблених книг
        with open('favorite_books.json', 'r') as f:
            favorite_books = json.load(f)
    except FileNotFoundError:
        return

    # Повертаємо список улюблених книг даного користувача
    return favorite_books.get(str(user_id), [])
