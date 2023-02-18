import config
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType


#Log
logging.basicConfig(level=logging.INFO)

#init
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)

#Цена
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=100*100) #Цена в копейках

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    #При нажатии старт отсылать стикер
    sti = open('static/sticker.webp', 'rb')
    await bot.send_sticker(message.chat.id, sti)
#Создаем 2 кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton("/Buy Купить/продлить подписку")

    markup.add(item1)

    #При нажатии старт сообщение, текст после "" это как раз создание клавиатуры в телеге
    await bot.send_message(message.from_user.id, f"Добро пожаловать, {message.from_user.full_name} \nтут можно оформить подписку Spotify^-^".format(message.from_user,
                                                                                                                                                    await bot.get_me()), parse_mode='html', reply_markup=markup)
# покупка
@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):

    await bot.send_invoice(message.chat.id,
                           title="Подписка spotify",
                           description= "Покупка/продление подписки spotify на месяц",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://ic.wampi.ru/2023/02/18/photo_2021-08-27_20-39-27.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")

#pre chekout(проверка перед платежем (ответ должен быть в течении 10 сек)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

#Успешный платеж
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("Честный выигрыши - 1xbet:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно")

#Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)





