import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from config_reader import config
from aiogram.types import Message
from inf import make_row_keyboard, menu1
import time
from random import randint


form_router = Router()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

class Form(StatesGroup):
    cash = State()
    kotika = State()
    choozing_menu1 = State()
    choozing_bets = State()
    choozing_bets_sum = State()


@dp.message(Command("start"))
async def cmd_start(message: Message, state):
    await state.update_data(cash=100)
    await state.set_state(Form.choozing_menu1)
    await message.answer(
        text="Привет!\nДобро пожаловать в Казино Имени Папича",
        reply_markup=make_row_keyboard(menu1)
    )

@dp.message(Form.choozing_menu1, F.text.in_(menu1))
async def menu1choosen(message: Message, state):
    b = message.text
    if b == 'Профиль':
        a = await state.get_data()
        await message.reply(f'Баланс: {a["cash"]}$')
    elif b == 'Сделать ставку':
        await state.set_state(Form.choozing_bets)
        await message.answer(
            text="Идет ожесточенная битва Котика против Песика\nНа кого желаете поставить?",
            reply_markup=make_row_keyboard(['Котик', 'Песик'])
        )

@dp.message(Form.choozing_bets, F.text.in_(['Котик', 'Песик']))
async def betschoosen(message: Message, state):
    b = message.text
    if b == 'Котик':
        await state.update_data(kotika=True)
    else:
        await state.update_data(kotika=False)
    await message.reply('Сколько желаете поставить?')
    await state.set_state(Form.choozing_bets_sum)

@dp.message(Form.choozing_bets_sum, lambda message: message.text.isdigit() == True)
async def procees(message: Message, state):
    data = await state.get_data()
    a = int(message.text)
    b = data['cash']
    if a > b:
        await message.reply('Не хватает баланса')
    else:
        msg = await message.reply('-')
        for i in range(20,0,-1):
            await msg.edit_text('🐱'+('-'*i)+'🐶')
            time.sleep(0.001)
        winnerkot = True
        if randint(0,1) == 0:
            await msg.edit_text('🐱')
        else:
            winnerkot = False
            await msg.edit_text('🐶')

        if winnerkot == data['kotika']:
            await state.update_data(cash=b+a)
        else:
            await state.update_data(cash=b-a)
        await state.set_state(Form.choozing_menu1)
        await message.answer(
            text="Желаете что нибудь еще?",
            reply_markup=make_row_keyboard(menu1)
        )


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())