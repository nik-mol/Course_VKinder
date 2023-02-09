import configparser

from vkbottle.bot import Bot, Message
from vkbottle import CtxStorage, BaseStateGroup, Keyboard, KeyboardButtonColor, Text
from scripts.vk_user import VkUser
from database.vkinder_db import add_user_to_db
from scripts import utils


config = configparser.ConfigParser()
config.read('settings.ini')
group_token = config['VK']['group_token']

group_bot = Bot(token=group_token)
ctx = CtxStorage()

keyboard = (Keyboard(one_time=True)
                .add(Text('Next', {"cmd": "next"}), color=KeyboardButtonColor.PRIMARY)
                .row()
                .add(Text('Block', {"cmd": "block"}), color=KeyboardButtonColor.NEGATIVE)
                .add(Text('Show favorites', {"cmd": "show"}), color=KeyboardButtonColor.SECONDARY)
                .add(Text('Favorites', {"cmd": "add"}), color=KeyboardButtonColor.POSITIVE))


@group_bot.on.message(text='/start')
async def create_user(message: Message):
    """
    Creates VkUser and shows an option.
    :param message: incoming message from user
    :return:
    """
    user = await group_bot.api.users.get(message.from_id, fields=['sex', 'city'])
    if message.from_id not in VkUser.user_dict:
        VkUser.user_dict[message.from_id] = VkUser(user[0].id, user[0].sex.value, user[0].city.id if user[0].city else None)
        add_user_to_db(user[0].id, user[0].first_name, user[0].last_name, user[0].sex.value)
    await first_launch(message)


async def first_launch(message: Message):
    """
    Defines parameters for search.
    :param message: incoming message
    :return:
    """
    vk_user = VkUser.user_dict[message.from_id]
    if not vk_user.city:    # if city was not defined in user profile
        await message.answer('Введите город для поиска:')
        await group_bot.state_dispenser.set(message.peer_id, RegData.CITY)
    elif not vk_user.age_from:
        await message.answer('Введите диапазон поиска по возрасту.\nВозраст от:')
        await group_bot.state_dispenser.set(message.peer_id, RegData.AGE_FROM)
    else:
        await next_option(message)


@group_bot.on.message(payload={"cmd": "next"})
async def next_option(message: Message):
    """
    Shows next option.
    :param: message: incoming message
    :return:
    """
    vk_user = VkUser.user_dict[message.from_id]
    option = await utils.show_option(vk_user)
    await message.answer('\n'.join(option[:3]), attachment=option[3], keyboard=keyboard)


@group_bot.on.message(payload={"cmd": "add"})
async def add_favorite(message: Message):
    """
    Saves option to favorites.
    :param: message: incoming message
    :return:
    """
    vk_user = VkUser.user_dict[message.from_id]
    vk_user.add_favorite()
    await message.answer('добавлено в избранные', keyboard=keyboard)


@group_bot.on.message(payload={"cmd": "show"})
async def show_favorites(message: Message):
    """
    Shows favorites.
    :param message: incoming message
    :return:
    """
    vk_user = VkUser.user_dict[message.from_id]
    favorites = vk_user.show_favorites()
    await message.answer(favorites, keyboard=keyboard)


@group_bot.on.message(payload={"cmd": "block"})
async def block_option(message: Message):
    """
    Adds option to blacklist.
    :param message: incoming message
    :return:
    """
    vk_user = VkUser.user_dict[message.from_id]
    vk_user.block_option()
    await message.answer('добавлено в список заблокированных пользователей', keyboard=keyboard)


class RegData(BaseStateGroup):
    AGE_FROM = 0
    AGE_TO = 1
    CITY = 2


@group_bot.on.message(state=RegData.AGE_FROM)
async def age_from(message: Message):
    """
    Defines parameter 'age_from' for search.
    :param message: incoming message
    :return:
    """
    if message.text.isdigit():
        ctx.set('age_from', message.text)
        await group_bot.state_dispenser.set(message.peer_id, RegData.AGE_TO)
        VkUser.user_dict[message.from_id].age_from = message.text
        await message.answer('Возраст до:')
    else:
        await message.answer('Ввод с клавиатуры должен содержать только цифры')
        await group_bot.state_dispenser.set(message.peer_id, RegData.AGE_FROM)


@group_bot.on.message(state=RegData.AGE_TO)
async def age_to(message: Message):
    """
    Defines parameter 'age_to' for search.
    :param message: incoming message
    :return:
    """
    if message.text.isdigit():
        ctx.set('age_to', message.text)
        VkUser.user_dict[message.from_id].age_to = message.text
        await first_launch(message)
    else:
        await message.answer('Ввод с клавиатуры должен содержать только цифры')
        await group_bot.state_dispenser.set(message.peer_id, RegData.AGE_TO)


@group_bot.on.message(state=RegData.CITY)
async def city(message: Message):
    """
    Defines parameter 'city' for search.
    :param message:
    :return:
    """
    cities = await utils.get_city_id(message.text)
    if cities:
        if cities.count == 1 or cities[0].title.lower() == message.text.lower():
            ctx.set('city', message.text)
            VkUser.user_dict[message.from_id].city = cities[0].id
            await message.answer(f'Выбран город: {cities[0].title}')
            await first_launch(message)
        else:
            await message.answer(
                f'Пожалуйста уточните какой именно город ваш:\n {", ".join(city.title for city in cities)}.')
            await group_bot.state_dispenser.set(message.peer_id, RegData.CITY)
    else:
        await message.answer('Такой город не найден, попробуйте еще раз')
        await group_bot.state_dispenser.set(message.peer_id, RegData.CITY)


if __name__ == '__main__':
    group_bot.run_forever()
