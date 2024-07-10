from functools import partial

import telebot

from config import TOKEN
from messages import start_message, help_message, add_book_message
from add_book import add_book
from read_book import read_book, send_random_book, send_format_buttons, add_favorite_book_after_read, \
                      delete_favorite_book, list_favorite_books, add_favorite_book


bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()


# Обробник команди /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name
    print(f'[INFO] [{user_name}]  handle_start function is called')
    bot.send_message(message.chat.id, start_message)


# Обробник команди /help
@bot.message_handler(commands=['help'])
def handle_help(message):
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name
    print(f'[INFO] [{user_name}]  handle_help function is called')
    bot.send_message(message.chat.id, help_message)


# Обробник команди /add_book
@bot.message_handler(commands=['add_book'])
def handle_add_book(message):
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name
    print(f'[INFO] [{user_name}]  add_book function is called')
    msg = bot.reply_to(message, add_book_message)
    # Додавання кнопки для повернення назад
    markup = telebot.types.InlineKeyboardMarkup()
    itembtn1 = telebot.types.InlineKeyboardButton('Скасувати', callback_data='cancel_add_book')
    markup.add(itembtn1)
    button = bot.send_message(message.chat.id, 'Натисніть кнопку \'Скасувати\', щоб скасувати надсилання книги',
                     reply_markup=markup)
    bot.register_next_step_handler(msg, partial(add_book, bot, button.message_id))


# Обробник команди /read_book
@bot.message_handler(commands=['read_book'])
def handle_read_book(message):
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name
    print(f'[INFO] [{user_name}]  read_book function is called')
    # Додавання 2-х кнопок (конкретна книга або випадкова)
    markup = telebot.types.InlineKeyboardMarkup()
    itembtn1 = telebot.types.InlineKeyboardButton('Так, знаю', callback_data='read_book_specific')
    itembtn2 = telebot.types.InlineKeyboardButton('Ні, хочу будь-що', callback_data='read_book_random')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, 'Ви знаєте, що хочете почитати ?', reply_markup=markup)


# Обробник команди /favorite_books
@bot.message_handler(commands=['favorite_books'])
def handle_list_favorite_books(message):
    user_name = message.from_user.username if message.from_user.username else message.from_user.first_name
    print(f'[INFO] [{user_name}]  favorite_books function is called')
    # Додавання 3-х кнопок (додати книгу, видалити книгу, подивитися список)
    markup = telebot.types.InlineKeyboardMarkup()
    itembtn1 = telebot.types.InlineKeyboardButton('Додати книгу в список', callback_data='add_favorite_book')
    itembtn2 = telebot.types.InlineKeyboardButton('Видалити книгу зі списку', callback_data='delete_favorite_book')
    itembtn3 = telebot.types.InlineKeyboardButton('Подивитися список', callback_data='list_favorite_books')
    markup.row(itembtn1, itembtn2)
    markup.row(itembtn3)
    bot.send_message(message.chat.id, 'Ви хочете зробити зі списком улюблених книг ?', reply_markup=markup)


# Обробник callback_data
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ['cancel_add_book', 'cancel_delete_book']:
        bot.answer_callback_query(call.id, 'Ви скасували надсилання книги')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    
    elif call.data == 'read_book_specific':
        msg = bot.send_message(call.message.chat.id, 'Введіть назву книги, яку ви хочете почитати')
        bot.register_next_step_handler(msg, partial(read_book, bot))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    elif call.data == 'read_book_random':
        send_format_buttons(bot, call.message.chat.id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    
    elif call.data.startswith('read_book_random_'):
        send_random_book(bot, call.message.chat.id, call.message.message_id, call)

    elif call.data == 'add_favorite_book_after_read':
        add_favorite_book_after_read(bot, call.from_user.id, call.message.chat.id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == 'cancel_add_favorite_book_after_read':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == 'add_favorite_book':
        txt = 'Будь ласка, перешліть файл книги, яку ви хочете додати до списку улюблених'
        msg = bot.send_message(call.message.chat.id, txt)
        bot.register_next_step_handler(msg, partial(add_favorite_book, bot, call.from_user.id, call.message.chat.id))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == 'delete_favorite_book':
        favorite_books = list_favorite_books(call.message.chat.id)
        if favorite_books:
            books_str = '\n'.join(f'{i+1}. {book}' for i, book in enumerate(favorite_books))
            books_str = books_str.replace('!!!', ' ').replace('_', ' ')
            bot.send_message(call.message.chat.id, f'Список улюблених книг:\n{books_str}')
        else:
            bot.send_message(call.message.chat.id, 'Список порожній \nВидаляти нічого')
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            return
        delete_favorite_book_message = 'Введіть номер книги зі списку улюблених, тої книги, яку Ви хочете видалити'
        msg = bot.send_message(call.message.chat.id, delete_favorite_book_message)
        bot.register_next_step_handler(msg, partial(delete_favorite_book, bot, call.message.chat.id))
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    elif call.data == 'list_favorite_books':
        favorite_books = list_favorite_books(call.message.chat.id)
        if favorite_books:
            books_str = '\n'.join(f'{i+1}. {book}' for i, book in enumerate(favorite_books))
            books_str = books_str.replace('!!!', ' ').replace('_', ' ')
            bot.send_message(call.message.chat.id, f'Список улюблених книг:\n{books_str}')
        else:
            empty_list_favorite_books = 'Список порожній \nДодайте книги за допомогою команди /favorite_books'
            bot.send_message(call.message.chat.id, empty_list_favorite_books)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


# Обробник не команд
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, 'Я розумію лише команди')


if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand('/start', 'Привітання'),
        telebot.types.BotCommand('/help', 'Інструкція по використанню бота'),
        telebot.types.BotCommand('/favorite_books', 'Список улюблених книг'),
        telebot.types.BotCommand('/add_book', 'Додати книгу'),
        telebot.types.BotCommand('/read_book', 'Скачати книгу'),
        ])
    bot.polling(none_stop=True)
