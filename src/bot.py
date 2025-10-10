import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self._register_handlers()
    
    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.message()(self.echo_message)
    
    async def cmd_start(self, message: Message):
        logger.info(f"Command /start from user {message.from_user.id}")
        await message.answer("Привет! Я эхо-бот. Отправь мне любое сообщение!")
    
    async def echo_message(self, message: Message):
        logger.info(f"Received message from user {message.from_user.id}: {message.text}")
        await message.answer(message.text)
    
    async def start(self):
        logger.info("Bot started successfully")
        await self.dp.start_polling(self.bot)

