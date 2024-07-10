import re
import os
from functools import partial


def check_file_exists(bot, button_message_id, message):
    if message.document is None:
        msg = bot.reply_to(message, 'Будь ласка, надішліть файл')
        bot.register_next_step_handler(msg, partial(add_book, bot, button_message_id))
        return False
    return True


def check_format(mime_type):
    # Список допустимих форматів
    valid_formats = ['application/pdf', 'application/x-fictionbook+xml', 'application/epub+zip',
                     'application/x-mobipocket-ebook', 'application/vnd.amazon.ebook', 'text/plain']
    return mime_type in valid_formats


def check_file_format(bot, button_message_id, message):
    if not check_format(message.document.mime_type):
        available_formats = 'PDF, FB2, EPUB, MOBI, AZW, AZW3, TXT'
        msg = bot.reply_to(message, f'Будь ласка, надішліть файл у одному з наступних форматів: {available_formats}')
        bot.register_next_step_handler(msg, partial(add_book, bot, button_message_id))
        return False
    return True


def check_filename(filename):
    # Регулярний вираз для перевірки формату назви файлу
    pattern = r'^(.*)!!!(.*)!!!(\d{4})!!!(.*)$'
    return re.match(pattern, filename) is not None


def check_file_name(bot, button_message_id, message):
    if not check_filename(message.document.file_name):
        correct_format = 'Назва книги!!!Автор!!!Рік видання!!!Жанр'
        msg = bot.reply_to(message, f'Будь ласка, надішліть файл з назвою у форматі: \n{correct_format}')
        bot.register_next_step_handler(msg, partial(add_book, bot, button_message_id))
        return False
    return True


def download_file(bot, message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(os.path.join('Books', message.document.file_name), 'wb') as new_file:
        new_file.write(downloaded_file)


def add_book(bot, button_message_id, message):
    if not check_file_exists(bot, button_message_id, message):
        return

    if not check_file_format(bot, button_message_id, message):
        return

    if not check_file_name(bot, button_message_id, message):
        return

    download_file(bot, message)

    bot.send_message(message.chat.id, 'Книгу додано до електронної бібліотеки\nДякуємо за використання нашого сервісу!')
    # bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    bot.delete_message(chat_id=message.chat.id, message_id=button_message_id)
    