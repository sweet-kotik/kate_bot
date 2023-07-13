import datetime
import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, StateFilter, Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (Message, KeyboardButton, 
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)

# токен бота
BOT_TOKEN = '5814309558:AAFrAqL0mNQHOX7V3c9uIc2-VvIIQo9kAvA'

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Создаем объекты бота и диспетчера
bot: Bot = Bot(BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Cоздаем класс и группы состояний 
class FSMFillForm(StatesGroup):
    first_state = State()        # Состояние ожидания ввода ответа
    second_state = State()        # Состояние ожидания ввода ответа

# Создаем объекты кнопок
button_1: KeyboardButton = KeyboardButton(text='_Приступить к вопросам_')
button_2: KeyboardButton = KeyboardButton(text='_Да_')
button_3: KeyboardButton = KeyboardButton(text='_Нет_')
button_4: KeyboardButton = KeyboardButton(text='_Получить вопрос_')

# Создаем объект клавиатуры, добавляя в него кнопки
keyboard_1: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_1]],
                                    resize_keyboard=True)

keyboard_2: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_2, button_3]],
                                    resize_keyboard=True)
keyboard_3: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
                                    keyboard=[[button_4]],
                                    resize_keyboard=True)

# инициализируем данные файла json
with open('question.json', 'r', encoding='utf-8') as f:
    # присваиваем хранимые данные переменной questions
    questions = json.load(f)

a: int = 0

# Этот хэндлер будет срабатывать на команду /start вне состояний
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    global a
    a = 0
    await message.answer(text='Здравствуй, я бот вопросов для познания себя\n\n'
                         'Если хочешь узнать мою задачу, отправь /info\n'
                         'Посмотреть перечень команд - команда /help\n'
                         'Чтобы получить первый вопрос кликни на кнопку "_Приступить к вопросам_"',  
                         reply_markup=keyboard_1)


# Этот хэндлер будет срабатывать на команду "/stop" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@dp.message(Command(commands='stop'), ~StateFilter(default_state))
async def process_stop_command_state(message: Message, state: FSMContext):
    global a
    await message.answer(text='Вы больше не будете получать оповещения\n Чтобы возобновить работу бота отправте командк /start')
    a += 1
    # Сбрасываем состояние
    await state.clear()


# Этот хэндлер будет срабатывать на команду /help
@dp.message(Command(commands='help'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(text='Перечень доступных команд:\n'
                        '/info - в чем заключается задача бота; \n'
                        '/stop - прервать работу бота (отправку им вопросов);\n'
                        '/start - начать/возобновить работу бота; \n'
                        '/help - перечень доступных команд. \n')


# Этот хэндлер будет срабатывать на команду /info
@dp.message(Command(commands='info'))
async def process_info_command(message: Message, state: FSMContext):
    await message.answer(text='Задачей вопросов является познание самого себя, '
                        'своего характера, слабостей и наоборот, сильных сторон, '
                        'необходимо постоянно прислушиваться к собственным желаниям, чувствам, мыслям.')


# Этот хэндлер будет срабатывать при нажатии кнопки "Приступить к вопросам"
@dp.message(Text(text=['_Приступить к вопросам_']))
async def questions_def(message: Message, state: FSMContext):
    await message.answer(text='Отправка вопросов будет происходить автоматически раз в день, вы согласны?\n'
                         'Отправка может быть прекращена в любой момент по команде /stop',
                         reply_markup=keyboard_2)
    await state.set_state(FSMFillForm.first_state)
   
# Этот хэндлер будет срабатывать при нажатии кнопки "_Да_"
@dp.message(StateFilter(FSMFillForm.first_state),
            lambda x:  x.text == '_Да_')
async def yes_def(message: Message, state: FSMContext):
    global a
    while a > -1:
        day = datetime.datetime.now()
        d = int(day.strftime("%d")) - 1
        d_1 = str(d+1)
        if a > 0:
            break
        else:
            await message.answer(questions[d][d_1],
                                 reply_markup=ReplyKeyboardRemove())
            await asyncio.sleep(86400)

# Этот хэндлер будет срабатывать при нажатии кнопки "_нет_"
@dp.message(StateFilter(FSMFillForm.first_state),
            lambda x:  x.text == '_Нет_')
async def no_def(message: Message, state: FSMContext):
    await message.answer(text='Вы отказались от автоматической отправки вопросов\n'
                         'Теперь вы можете самостоятельно регулировать их получения кликая по кнопке "_Получить вопрос_"',
                         reply_markup=keyboard_3)
    await state.set_state(FSMFillForm.second_state)

# Этот хэндлер будет срабатывать при нажатии кнопки "_нет_"
@dp.message(StateFilter(FSMFillForm.second_state),
            lambda x:  x.text == '_Получить вопрос_')
async def questions_two_def(message: Message, state: FSMContext):
    day = datetime.datetime.now()
    d = int(day.strftime("%d")) - 1
    d_1 = str(d+1)
    await message.answer(questions[d][d_1],
                         reply_markup=keyboard_3)


# Запускаем поллинг
if __name__ == '__main__':
    dp.run_polling(bot)
