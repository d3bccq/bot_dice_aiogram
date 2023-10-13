#Бот работает на версии aiogram 2.25.1 и желательно python 10-11 версии
#Укажите свой токен в cfg файле


import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher.filters import BoundFilter
from asyncio import sleep
import cfg
from aiogram.types import ChatPermissions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.builtin import Text, Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData
import db


#Вывод сообщения в консоль
async def on_sturtup(_):
    db.sq.connect("db/database.db")
print("Подключён к БД")
print("Я ЖИВОЙ ОРИГИНАЛ")
 

#Переменные с привилегиями для мута и размута
perms1 = ChatPermissions()
perms2 = ChatPermissions(can_send_audios=True, can_add_web_page_previews=True, can_change_info=True, can_invite_users=True, can_manage_topics=True, can_pin_messages=True, can_send_documents=True, an_send_media_messages=True, can_send_messages=True, can_send_other_messages=True, can_send_photos=True, can_send_polls=True, can_send_video_notes=True, can_send_videos=True, can_send_voice_notes=True)

#ЛОГИН
logging.basicConfig(level=logging.INFO)

#Сам бот
bot = Bot(token = cfg.TOKEN2) #Ваш токен
dp = Dispatcher(bot, storage=MemoryStorage())


#Клавиатура для добавления бота в чат
ikb = InlineKeyboardMarkup(row_width=1)
ikb1 = InlineKeyboardButton(text="Нажми чтобы добавить бота в чат",
                            url='https://telegram.me/mutekub_bot?startgroup=new')
ikb.add(ikb1)


#Блок антиспама взятый полностью с официальной документации
def rate_limit(limit: int, key=None):

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator

class ThrottlingMiddleware(BaseMiddleware):

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        
        handler = current_handler.get()

        
        dispatcher = Dispatcher.get_current()
        
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            
            await self.message_throttled(message, t)

            
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        
        delta = throttled.rate - throttled.delta

        #Тут указывать задержку для антиспама (вместо 10)
        if throttled.exceeded_count <= 10:
            await message.delete()
            await message.answer(None)
           

        
        await asyncio.sleep(delta)

        
        thr = await dispatcher.check_key(key)

        # Вместо None можете вписать своё ответное сообщение по истечению таймера на мут
        if thr.exceeded_count == throttled.exceeded_count:
            await message.answer(None)


#@Rate_limit надо укащывать перед блоком команд для работы антиспама, можно поменять значение с 5 на другое

#Вывод ифнормации о боте
@rate_limit(5)
@dp.message_handler(commands=['INFO'])
async def help_command(message: types.Message):
  if message.chat.type == 'private':
    #await bot.send_message(chat_id=1,text="@"f"{message.from_user.username} <b>"f"[{message.from_user.full_name}]</b> Узнаёт информацию в лс", parse_mode="html") #Это как пример чтобы вы могли видеть что пользователи делают с вашим ботом. Вместо 1 укажите id чата куда должен писать бот
    await message.answer(text=cfg.HELP_COMMAND, reply_markup=ikb)
  if message.chat.type == 'supergroup':
    #await bot.send_message(chat_id=1,text="@"f"{message.from_user.username} <b>"f"[{message.from_user.full_name}]</b> Узнаёт информацию в чате", parse_mode="html") #Это как пример чтобы вы могли видеть что пользователи делают с вашим ботом. Вместо 1 укажите id чата куда должен писать бот
    await message.answer(text=cfg.HELP_COMMAND, reply_markup=ikb)


#Команда для вывода статистики
@dp.message_handler(commands=["stats"])
async def statik(message: types.Message):
  if message.chat.type == 'private':    
      cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
      row = cursor.fetchone()
      if row is None:
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win)) создание таблицы если челвоек первый раз узнает статистику
        await message.reply("❗️У тебя еще нет статистики, кинь кубик❗️")
      elif row is not None:
        losse1 = db.cur.execute (f"SELECT losse INTEGER FROM winka WHERE user_id == '{message.from_user.id}'")
        show1 = losse1.fetchall()
        show1 = show1[0][0]
        win1 = db.cur.execute (f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'")
        show2 = win1.fetchall()
        show2 = show2[0][0]
        await message.reply(f'✨{message.from_user.full_name}✨\n\n🏆Ты победил: {show2} раз\n☠️Ты проиграл: {show1} раз')
  if message.chat.type == 'supergroup':
      cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
      row = cursor.fetchone()
      if row is None:
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win)) создание таблицы если челвоек первый раз узнает статистику
        await message.reply("❗️У тебя еще нет статистики, кинь кубик❗️")
      elif row is not None:
        losse1 = db.cur.execute (f"SELECT losse INTEGER FROM winka WHERE user_id == '{message.from_user.id}'")
        show1 = losse1.fetchall()
        show1 = show1[0][0]
        win1 = db.cur.execute (f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'")
        show2 = win1.fetchall()
        show2 = show2[0][0]
        await message.reply(f'✨{message.from_user.full_name}✨\n\n🏆Ты победил: {show2} раз\n☠️Ты проиграл: {show1} раз')
     
        
#Проверка на админа для мута
class MyFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() or  message.from_user.id == 111 #Вместо 111 можете указать свой айди и бот будет считать вас админом

dp.filters_factory.bind(MyFilter)

#Команда мута если пользователь админ
@rate_limit(2)
@dp.message_handler(commands=["mute"], commands_prefix='/', is_admin=True)
async def hard_mute(message: types.Message):
  if message.chat.type == 'private':
    await message.reply("Эта команда только для чата")
  if message.chat.type == 'supergroup' and not message.reply_to_message:
    await message.reply("Эта команда должна быть ответом на сообщение") 
  elif message.reply_to_message:  
    await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, perms1)
    await message.answer(text=f"({message.reply_to_message.from_user.full_name})   @{message.reply_to_message.from_user.username}\n\n☠️Тебе вставили кляп на пожизнено!☠️")
  return hard_mute

#Команда мута если пользователь не админ
@rate_limit(2)
@dp.message_handler(commands=["mute"], commands_prefix='/')
async def hard_mute1(message: types.Message):
  if message.chat.type == 'private':
    await message.reply("Эта команда только для чата")
  if message.chat.type == 'supergroup':
    await message.reply("У вас нет доступа к этой команде")
  return hard_mute1
        
#Команда размута если пользователь админ
@rate_limit(2)
@dp.message_handler(commands=["unmute"], commands_prefix='/', is_admin=True)
async def unmute(message: types.Message):
  if message.chat.type == 'private':
     await message.reply("Эта команда только для чата")
  if message.chat.type == 'supergroup' and not message.reply_to_message:
    await message.reply("Эта команда должна быть ответом на сообщение")
  elif message.reply_to_message:  
      await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, perms2)
      await message.answer(text=f"({message.reply_to_message.from_user.full_name})   @{message.reply_to_message.from_user.username}\n\n🕊Тебе вытащили кляп!🕊")
  return unmute

#Команда рамута если пользователь не админ
@rate_limit(2)
@dp.message_handler(commands=["unmute"], commands_prefix='/')
async def unmute1(message: types.Message):
  if message.chat.type == 'private':
     await message.reply("Эта команда только для чата")
  if message.chat.type == 'supergroup':
     await message.reply("У вас нет доступа к этой команде")
  return unmute1
         
#Стикер на слово "Мяу"   
@dp.message_handler(Text('мяу'))
async def meow(message: types.Message):
      print(await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEJFblkbR2sqlRnT9Ac04s5Xvel3ViVSAACURkAAnFS-EtvrNccpDBEai8E"))
      await message.delete()
      return meow

#Стикер на слово "Мяу" но другой  
@dp.message_handler(Text('Мяу'))
async def Meow(message: types.Message):
      await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEJ4GNkyO0OnOHDyGiLQfHWVR6kXLfmcwACHBgAAgtAaEhBHgEr23Yjcy8E")
      await message.delete()
      return Meow

#Стикер на Эмодзи   
@dp.message_handler(Text('✌️'))
async def hi(message: types.Message):
      await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEJSI9khgHkOk783T4sHwGwdoIgGHDaXwADLgACJ1EwSVBao9ZuouNKLwQ")
      return hi

#Стикер на Эмодзи 
@dp.message_handler(Text('🦄'))
async def poni(message: types.Message):
      await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEJSJFkhgL9ZcpZO_qkKSoIFTQLQaaCmgAC_y4AAmdD-Uopwlkzh7zYoS8E")
      return poni

#Стикер на Эмодзи
@dp.message_handler(Text('🧟'))
async def zombe(message: types.Message):
      await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEJSJNkhgMwUamFn1-5kmaywdvqF9HUwQAC4CcAAs1z8UisGGmMME2BXC8E")
      return zombe


#Блок с кубами
kukb1 = ("!Куб 1", "!куб 1") 
@rate_limit(5)
@dp.message_handler(Text (kukb1))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
    cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
    row = cursor.fetchone()
    if row is None:
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win)) Создаёт БД с нулями
      await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️")
    elif row is not None:
      result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'") # db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) Берёт значения  из БД
      perem = result_losse.fetchall()[0][0]
      result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
      perem2 = result_win.fetchall()[0][0]
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 1 < kub:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
      elif 1 > kub: 
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                           
      else:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 1 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 1 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")              

kukb2 = ("!Куб 2", "!куб 2") 
@rate_limit(5)
@dp.message_handler(Text (kukb2))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
    cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
    row = cursor.fetchone()
    if row is None:
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win))
      await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️")
    elif row is not None:
      result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
      perem = result_losse.fetchall()[0][0]
      result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
      perem2 = result_win.fetchall()[0][0]
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 2 < kub:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
      elif 2 > kub:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()  
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                              
      else:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 2 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 2 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")              


kukb3 = ("!Куб 3", "!куб 3") 
@rate_limit(5)
@dp.message_handler(Text (kukb3))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
    cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
    row = cursor.fetchone()
    if row is None:
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win))
      await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️")
    elif row is not None:
      result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
      perem = result_losse.fetchall()[0][0]
      result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
      perem2 = result_win.fetchall()[0][0]
      db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 3 < kub:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
      elif 3 > kub:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()   
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
        await sleep(600)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                            
      else:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
        db.db.commit()
        await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 3 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 3 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")              


kukb4 = ("!Куб 4", "!куб 4") 
@rate_limit(5)
@dp.message_handler(Text (kukb4))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
      cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
      row = cursor.fetchone()
      if row is None:
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win))
        await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️") 
      elif row is not None:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        perem = result_losse.fetchall()[0][0]
        result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
        perem2 = result_win.fetchall()[0][0]
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
        kub = await bot.send_dice(message.chat.id)
        kub = kub['dice']['value']
        await sleep (4)
        if 4 < kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
        elif 4 > kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit() 
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                              
        else:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}") 
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 4 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 4 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")       

kukb5 = ("!Куб 5", "!куб 5") 
@rate_limit(5)
@dp.message_handler(Text (kukb5))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
      cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
      row = cursor.fetchone()
      if row is None:
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win))
        await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️")
      elif row is not None:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        perem = result_losse.fetchall()[0][0]
        result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
        perem2 = result_win.fetchall()[0][0]
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
        kub = await bot.send_dice(message.chat.id)
        kub = kub['dice']['value']
        await sleep (4)
        if 5 < kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
        elif 5 > kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit() 
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                             
        else:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 5 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 5 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}")   
         
kukb6 = ("!Куб 6", "!куб 6") 
@rate_limit(5)
@dp.message_handler(Text (kukb6))
async def cub2(message: types.Message):
  if message.chat.type == 'supergroup': #Если сообщение в чате
      cursor = db.cur.execute(f"SELECT user_id FROM winka WHERE user_id == '{message.from_user.id}'")
      row = cursor.fetchone()
      if row is None:
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = 0, win = 0) # cursor = db.execute('INSERT INTO table_name (user_id, username, losse, win) VALUES (?, ?, ?, ?)',(user_id, username, losse, win))
        await message.reply("❗️Ты кидаешь кубик в первый раз, по этому напиши ещё разок❗️")
      elif row is not None:
        result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
        perem = result_losse.fetchall()[0][0]
        result_win = db.cur.execute ((f"SELECT win FROM winka WHERE user_id == '{message.from_user.id}'"))
        perem2 = result_win.fetchall()[0][0]
        db.db_table_val(user_id=message.from_user.id, username=message.from_user.username, losse = perem, win = perem2)
        kub = await bot.send_dice(message.chat.id)
        kub = kub['dice']['value']
        await sleep (4)
        if 6 < kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
        elif 6 > kub:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET losse = losse + 1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit() 
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n⛔️Теперь у тебя мут на 10 минут")
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
          await sleep(600)
          await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)                                                              
        else:
          result_losse = db.cur.execute (f"SELECT losse FROM winka WHERE user_id == '{message.from_user.id}'")
          db.cur.execute(f"UPDATE winka SET win = win +1 WHERE user_id == '{message.from_user.id}'")
          db.db.commit()
          await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}") 
  elif message.chat.type == 'private': #Если сообщение в лс бота
      kub = await bot.send_dice(message.chat.id)
      kub = kub['dice']['value']
      await sleep (4)
      if 6 < kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      elif 6 > kub:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n☠️Тебе не повезло!\n👐Выпало: {kub}\n👁В лс мута нет")
      else:
         await message.reply(text=f"✨{message.from_user.full_name}✨\n\n🏆ТЫ ПОБЕДИЛ!\n👐Выпало: {kub}") 

#Работа куба если пользователь не ввел число      
kukb = ("!Куб", "!куб")
@rate_limit(5)    
@dp.message_handler(Text(kukb))
async def cub_none(message: types.Message):
    await message.reply(text='⛔️Необходимо ввести число от 1 до 7')
    return cub_none

#Работа бота если кто-то написал 'Я люблю Путина'
@rate_limit(5)
@dp.message_handler(Text('Я люблю Путина'))
async def silent_Putin(message: types.Message):
    await message.reply(text= "А Путин никого не любит")
    await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms1)
    await sleep(30) #Мут на 30 секунд
    await bot.restrict_chat_member(message.chat.id, message.from_user.id, perms2)
    return silent_Putin


#Стикер на слова "Ты странный"
strann = ("Ты странный", "ты странный")
@dp.message_handler(Text(strann))
async def stran(message: types.Message):
      await bot.send_sticker(chat_id=message.chat.id,
                               sticker="CAACAgIAAxkBAAEKIFRk6OmvWvMZzoSlo3Yt1vjsLqYbNgAC9DYAArv0QUo5ytf2145SdjAE")
      return stran


 #!!!Фильтр на слова!!! Чтобы настроить укажите слова в cfg файле
@dp.message_handler(content_types='text')
async def filter(message: types.Message):
    text = message.text.lower()
    for word in cfg.WORDS:
            if word in text:
                await message.delete()


if __name__ == '__main__':
   dp.middleware.setup(ThrottlingMiddleware())


   executor.start_polling(dp, on_startup = on_sturtup, skip_updates=True)