import config
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType

import db

# Log
logging.basicConfig(level=logging.INFO)

# init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
dblya = db.DBlya()

antimammoth = {}  # База данных для проверки

# Цена
PRICE = types.LabeledPrice(
    label="Подписка на 1 месяц", amount=100 * 100
)  # Цена в копейках


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    # При нажатии старт отсылать стикер
    sti = open("static/sticker.webp", "rb")
    await bot.send_sticker(message.chat.id, sti)
    # Создаем 2 кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton("/buy Купить подписку")
    item2 = types.KeyboardButton("/extension Продлить подписку")

    markup.add(item1, item2)

    # При нажатии старт сообщение, текст после "" это как раз создание клавиатуры в телеге
    await bot.send_message(
        message.from_user.id,
        f"Добро пожаловать, {message.from_user.full_name} \nтут можно оформить подписку Spotify^-^".format(
            message.from_user, await bot.get_me()
        ),
        parse_mode="html",
        reply_markup=markup,
    )


# покупка
@dp.message_handler(commands=["buy"])
async def buy(message: types.Message):
    await bot.send_invoice(
        message.chat.id,
        title="Подписка spotify",
        description="Покупка подписки spotify на месяц",
        provider_token=config.PAYMENTS_TOKEN,
        currency="rub",
        photo_url="https://ic.wampi.ru/2023/02/18/photo_2021-08-27_20-39-27.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="one-month-subscription",
        payload="Buy",
    )


# pre chekout(проверка перед платежем (ответ должен быть в течении 10 сек)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# Успешный платеж
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("Честный выигрыши - 1xbet:")
    payment_info = message.successful_payment.to_python()
    print(message)  # Принт тут для вывода того, что происходит в консоль
    for k, v in payment_info.items():
        print(f"{k} = {v}")
    antimammoth[message.from_user.id] = True  # Оплатил
    login, password = dblya.get_free_login(message.from_user.id)
    await bot.send_message(
        message.chat.id,
        f"Платеж на сумму {message.successful_payment.total_amount // 100}"
        f" {message.successful_payment.currency} прошел успешно{',введите логин и пароль' if message.successful_payment.invoice_payload == 'Extension' else f', ваш логин{login} ваш пароль{password}'}",
    )
    # квадратные скобки и потом равно, чтобы проверить что произошло
    # и показать полностью строку или часть


# Продление
@dp.message_handler(commands=["extension"])
async def extension(message: types.Message):
    print(message)
    await bot.send_invoice(
        message.chat.id,
        title="Подписка spotify",
        description="Продление подписки spotify на месяц",
        provider_token=config.PAYMENTS_TOKEN,
        currency="rub",
        photo_url="https://ic.wampi.ru/2023/02/18/photo_2021-08-27_20-39-27.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="one-month-subscription",
        payload="Extension",
    )  # Вводим название того, что происходит оплата или продление


@dp.message_handler(commands=["credentials"])
async def get_credentials(message: types.Message):
    try:
        if antimammoth[message.from_user.id]:  # Проверка оплатил или нет
            arguments = message.get_args()
            arguments_splitted = arguments.split(" ")
            dblya.add_login(
                arguments_splitted[0], arguments_splitted[1], message.from_user.id
            )
            await bot.send_message(
                message.chat.id, text="Ожидайте, пока раб продлит вам подписку"
            )
        else:
            await bot.send_message(
                message.chat.id, text="Для начала оплатите подписку /extension"
            )
    except:
        await bot.send_message(
            message.chat.id,
            text="Повторите попытку позже или обратитесь к администратору /help (idi nahui)",
        )
    finally:
        antimammoth[message.from_user.id] = False


# Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
