# meta developer: @ferglab
# scope: ferglab 1.0.0
# scope: fegrlab 1.0.0

import logging
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.types import Message, PeerUser
from telethon.utils import get_display_name
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class WordBlockerMod(loader.Module):
    """Блокирует пользователей, которые отправили определённое слово в ЛС"""
    
    strings = {
        "name": "blockword",
        "config_word": "Слово, которое вызывает блокировку",
        "config_message": "Сообщение, которое отправляется перед блокировкой",
        "help": "Использование: .wordblocker <слово> <сообщение>",
        "word_set": "Слово и сообщение успешно настроены!",
        "no_word": "Слово не установлено. Используйте .wordblocker <слово> <сообщение> чтобы установить.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "trigger_word",
                "",
                lambda: "Слово, которое вызывает блокировку",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "block_message",
                "Вы были заблокированы за отправку запрещённого слова.",
                lambda: "Сообщение, которое отправляется перед блокировкой",
                validator=loader.validators.String(),
            ),
        )

    async def wordblockercmd(self, message):
        """<слово> <сообщение> - Настроить слово и сообщение для блокировки"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("help"))
            return
            
        parts = args.split(' ', 1)
        if len(parts) < 2:
            await utils.answer(message, self.strings("help"))
            return
            
        word = parts[0]
        message_text = parts[1]
        
        self.config["trigger_word"] = word
        self.config["block_message"] = message_text
        
        await utils.answer(message, self.strings("word_set"))

    async def watcher(self, message: Message):
        if (
            not isinstance(message, Message)
            or not isinstance(message.peer_id, PeerUser)
            or message.out
            or not self.config["trigger_word"]
        ):
            return

        # Проверяем, содержит ли сообщение наше слово (без учёта регистра)
        if self.config["trigger_word"].lower() in message.raw_text.lower():
            # Отправляем сообщение перед блокировкой
            try:
                await message.reply(self.config["block_message"])
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение блокировки: {e}")
            
            # Блокируем пользователя
            try:
                await self.client(BlockRequest(id=message.sender_id))
            except Exception as e:
                logger.error(f"Не удалось заблокировать пользователя: {e}")

            logger.info(f"Заблокирован пользователь {message.sender_id} за отправку '{self.config['trigger_word']}'")