import sqlite3
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token='6022329072:AAGUm7W5YskG5BA4X3MJK-5QMK4RxfFHXKk')
dp = Dispatcher(bot, storage=storage)
db = sqlite3.connect('server.db')
cursor = db.cursor()
data = {}
coefficient = 0.0
names_list = [
    [
        'United', 'Dinamo', 'Real',
    ],
    ['Abakan', 'Aginskoye', 'Almetyevsk', 'Anadyr', 'Anapa', 'Angarsk', 'Apatity', 'Arkhangelsk', 'Armavir', 'Arsenyev',
     'Artem', 'Arzamas', 'Asbest', 'Astrakhan', 'Achinsk', 'Balabanovo', 'Balakovo', 'Balashikha', 'Barnaul', 'Bataysk',
     'Belgorod', 'Belogorsk', 'Beloretsk', 'Belorechensk', 'Berdsk', 'Berezniki', 'Birobidzhan', 'Biysk',
     'Blagoveshchensk', 'Bor', 'Borisoglebsk', 'Bratsk', 'Bryansk', 'Bugulma', 'Buzuluk', 'Velikiy Novgorod',
     'Veliky Ustyug', 'Vladikavkaz', 'Vladimir', 'Vladivostok', 'Volgodonsk', 'Volgograd', 'Vologda', 'Volzhsk',
     'Vorkuta', 'Voronezh', 'Voskresensk', 'Votkinsk', 'Vsevolozhsk', 'Vyborg', 'Vyksa', 'Vyazma', 'Yakutsk',
     'Yaroslavl', 'Yegoryevsk', 'Yekaterinburg', 'Yelets', 'Yessentuki', 'Yoshkar-Ola', 'Zarechny', 'Zelenodolsk',
     'Zelenogorsk', 'Zheleznogorsk', 'Tver', 'Zheleznovodsk', 'Zhigulyovsk', 'Zhukovsky', 'Zlatoust',
     'Zvenigorod', 'Zyryanovsk']

]


class FSMBet(StatesGroup):
    ask_number = State()


kb_start = InlineKeyboardMarkup().add(InlineKeyboardButton(callback_data='info', text='Как это работает?'))
kb_info = InlineKeyboardMarkup().add((InlineKeyboardButton(callback_data='first_bet', text='Начать')))
kb_bet = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Сделать ставку на 1', callback_data='make_bet_1')],
    [InlineKeyboardButton('Сделать ставку на 2', callback_data='make_bet_2')],
    [InlineKeyboardButton('Поставить на ничью', callback_data='make_bet_draw_0')],
    [InlineKeyboardButton('Следующая ставка', callback_data='next_bet')],
    [InlineKeyboardButton('Закончить', callback_data='end')]
], row_width=1)
kb_final = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton('Следующая ставка', callback_data='first_bet')],
    [InlineKeyboardButton('Закончить', callback_data='end')]
])
kb_cancel = InlineKeyboardMarkup().add(InlineKeyboardButton(callback_data='end', text='Отмена'))
kb_ok = InlineKeyboardMarkup().add(InlineKeyboardButton(callback_data='ok', text='Ок'))


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    await message.answer('Привет! Этот бот позволит вам ставить несуществующие деньги на несуществующие футбольные '
                         'матчи и получать несуществующую прибыль!', reply_markup=kb_start)


async def change_db(user_id, name, cash=0.0, count=0, count_success=0, count_failure=0, income=0.0, loss=0.0,
                    total=0.0):
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id BIGINT,
        name TEXT,
        cash REAL,
        count BIGINT,
        count_success BIGINT,
        count_failure BIGINT,
        income REAL,
        loss REAL,
        total REAL
    )""")

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        updated_values = (
            user_data[2] + cash,
            user_data[3] + count,
            user_data[4] + count_success,
            user_data[5] + count_failure,
            user_data[6] + income,
            user_data[7] + loss,
            user_data[8] + total
        )
        cursor.execute(
            "UPDATE users SET cash=?, count=?, count_success=?, count_failure=?, income=?, loss=?, total=? WHERE id=?",
            (*updated_values, user_id))
    else:
        cash = 10000.0
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (user_id, name, cash, count, count_success, count_failure, income, loss, total))

    db.commit()


async def get_user_cash(user_id):
    cursor.execute("SELECT cash FROM users WHERE id=?", (user_id,))
    user_cash = cursor.fetchone()

    cash = round(user_cash[0], 2)
    if cash <= 0:
        cursor.execute("UPDATE users SET cash=200.0")
        db.commit()
        user_cash = cursor.fetchone()
        cash = round(user_cash[0], 2)
    return round(cash, 2)


async def is_number(stroka: str):
    try:
        float(stroka)
        return True
    except ValueError:
        return False


async def message_bet(callback: types.CallbackQuery):
    global data
    global coefficient
    if callback.data == 'first_bet':
        data = {}
    percent1 = round(random.uniform(1, 80), 2)
    percent2 = round(random.uniform(1, 100 - percent1), 2)
    percent_draw = round(100 - percent1 - percent2, 2)
    first_coefficient = round(1 / (percent1 / 100), 2)
    second_coefficient = round(1 / (percent2 / 100), 2)
    draw_coefficient = round(1 / (percent_draw / 100), 2)
    name = names_list[1][random.randint(0, 69)]
    name2 = name
    while name == name2:
        name2 = names_list[1][random.randint(0, 69)]
    if random.randint(1, 10) == 1:
        name = f'{names_list[0][random.randint(0, 2)]} {name}'
    if random.randint(1, 10) == 1:
        name2 = f'{names_list[0][random.randint(0, 2)]} {name}'
    winner = ''.join(random.choices([name, 'Ничья_0', name2],
                                    weights=[percent1 / 100, percent_draw / 100, percent2 / 100]))
    if winner == name:
        data.update({'number': 1})
        coefficient = first_coefficient
    elif winner == name2:
        data.update({'number': 2})
        coefficient = second_coefficient
    else:
        data.update({'number': 0})
        coefficient = draw_coefficient
    data.update({'winner': winner})
    if callback.data == 'first_bet':
        await callback.message.delete()
        msg = await bot.send_photo(chat_id=callback.message.chat.id, photo=open('football_pic.jpeg', 'rb'),
                                   reply_markup=kb_bet, caption=f'{name} VS {name2}\n'
                                                                f'1-я: {first_coefficient} Ничья: {draw_coefficient} '
                                                                f'2-я: {second_coefficient}')
        data.update({'msg': msg['message_id']})
    else:
        await bot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                       caption=f'{name} VS {name2}\n'
                                               f'1-я:{first_coefficient} Ничья:{draw_coefficient} '
                                               f'2-я:{second_coefficient}', reply_markup=kb_bet)


@dp.callback_query_handler(text='info')
async def info_callback(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                parse_mode='HTML', text='На ваш счёт будут зачислены 10000 нереальных рублей\n'
                                                        'Их вы можете ставить и получать определённую прибыль '
                                                        '(в зависимости от коэфицента)\n'
                                                        'Если не угадаете - вся сумма уйдет букмекеру\n'
                                                        'Если баланс уйдет в минус - добавим 200 рублей\n'
                                                        '(неограниченное количество раз)\n'
                                                        'Готовы?')
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=kb_info)


@dp.callback_query_handler(text=['first_bet', 'next_bet'])
async def start_bet_cycle(callback: types.CallbackQuery):
    await change_db(user_id=callback.from_user.id, name=callback.from_user.first_name)
    await message_bet(callback=callback)


@dp.callback_query_handler(text=['make_bet_1', 'make_bet_2', 'make_bet_draw_0'])
async def asking_amount(callback: types.CallbackQuery):
    global data
    data.update({'call': callback.data[-1]})
    await FSMBet.ask_number.set()
    await bot.edit_message_media(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                 media=InputMediaPhoto(open('cash.jpg', 'rb')))
    await bot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                   caption='Напишите сумму ставки:')
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=kb_cancel)


@dp.callback_query_handler(text='end', state=FSMBet.ask_number)
async def deleting(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    global data
    data = {}
    await callback.message.delete()


@dp.message_handler(state=FSMBet.ask_number)
async def results(message: types.Message, state: FSMContext):
    if ',' in message.text:
        await message.reply('Пожалуйста, пишите через точку')
    elif not await is_number(message.text):
        await message.reply('Пожалуйста, напишите сумму в виде числа (копейки указываются через точку)')
    elif await get_user_cash(user_id=message.from_user.id) < float(message.text):
        await message.reply('На вашем балансе недостаточно средств (если ваш баланс отрицательный,'
                            ' то на него автоматически зачисляются 200 рублей', reply_markup=kb_ok)
    else:
        global data, coefficient
        await state.finish()
        bet_summ = round(float(message.text), 2)
        winner_score = random.randint(1, 5)
        loser_score = random.randint(0, winner_score - 1)
        count = 1
        await message.delete()
        if data['number'] == 1:
            score = f'{winner_score}:{loser_score}'
        elif data['number'] == 2:
            score = f'{loser_score}:{winner_score}'
        else:
            score = f'{loser_score}:{loser_score}'
        if int(data['call']) == data['number']:
            count_success, count_failure = 1, 0
            cash = round(bet_summ * coefficient, 2)
            income = cash
            total = cash
            loss = 0
            await bot.edit_message_media(chat_id=message.chat.id, message_id=data['msg'],
                                         media=InputMediaPhoto(open('victory_pic.jpg', 'rb')))
            if str(data['winner']) != 'Ничья_0':
                await bot.edit_message_caption(chat_id=message.chat.id, message_id=data['msg'],
                                               caption=f"Вы победили!\n"
                                                       f"Команда {(data['winner'])} победила со счётом {score}\n"
                                                       f"+{cash} рублей\n")
            else:
                await bot.edit_message_caption(chat_id=message.chat.id, message_id=data['msg'],
                                               caption=f"Вы победили!\n"
                                                       f"Команды сыграли вничью со счётом {score}\n"
                                                       f"+{cash} рублей")

        else:
            count_success, count_failure = 0, 1
            cash = -bet_summ
            loss = cash
            income = 0
            total = cash
            await bot.edit_message_media(chat_id=message.chat.id, message_id=data['msg'],
                                         media=InputMediaPhoto(open('defeat_pic.jpg', 'rb')))
            if data['winner'] != 'Ничья_0':
                await bot.edit_message_caption(chat_id=message.chat.id, message_id=data['msg'],
                                               caption=f"Вы проиграли!\n"
                                                       f"Команда {str(data['winner'])} победила со счётом {score}\n"
                                                       f"{cash} рублей\n")
            else:
                await bot.edit_message_caption(chat_id=message.chat.id, message_id=data['msg'],
                                               caption=f"Вы проиграли!\n"
                                                       f"Команды сыграли вничью со счётом {score}\n"
                                                       f"{cash} рублей\n")

        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=data['msg'],
                                            reply_markup=kb_final)
        await change_db(user_id=message.from_user.id, name=message.from_user.first_name, cash=cash, count=count,
                        count_success=count_success, count_failure=count_failure, income=income, loss=loss, total=total)


@dp.callback_query_handler(text='end')
async def deleting(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    global data
    print(data)
    data = {}
    await callback.message.delete()


@dp.message_handler(commands='info')
async def info_message(message: types.Message):
    await message.answer(text='На ваш счёт будут зачислены 10000 нереальных рублей\n'
                              'Их вы можете ставить и получать определённую прибыль '
                              '(в зависимости от коэфицента)\n'
                              'Если не угадаете - вся сумма уйдет букмекеру\n'
                              'Если баланс уйдет в минус - добавим 200 рублей)\n'
                              '(неограниченное количество раз)', parse_mode='HTML', reply_markup=kb_ok)


@dp.callback_query_handler(text='ok')
async def ok_func(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.delete()


async def get_user_data(user_id, message: types.Message):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        cash = round(user_data[2], 2)
        count = user_data[3]
        count_success = user_data[4]
        count_failure = user_data[5]
        income = round(user_data[6], 2)
        loss = round(user_data[7], 2)
        total = round(user_data[8], 2)
        if total > 0:
            total = '+' + str(total)
        await message.answer(text=f"Статистика ставок:\n"
                                  f"Баланс: {cash}\n"
                                  f"Количество ставок: {count}\n"
                                  f"Количество выигрышей: {count_success}\n"
                                  f"Количество проигрышей: {count_failure}\n"
                                  f"Выиграно: +{income} рублей\n"
                                  f"Проиграно: {loss} рублей\n"
                                  f"Всего: {total} рублей", reply_markup=kb_ok)
    else:
        await message.answer(text=f"Я не могу отправить вам статистику, поскольку ещё не сделали ни единой ставки",
                             reply_markup=kb_ok)


@dp.message_handler(commands='statistics')
async def stats_func(message: types.Message):
    await get_user_data(user_id=message.from_user.id, message=message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
