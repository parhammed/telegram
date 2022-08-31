from telegram import Update, KeyboardButton as Btn, ReplyKeyboardMarkup, Message
from telegram.ext import Dispatcher, CallbackContext, CommandHandler, MessageHandler, Filters

from utils import IdManager, Database

_home = ReplyKeyboardMarkup([[Btn("دریافت لینک پیام ناشناس 🔗")]])
_send = ReplyKeyboardMarkup([[Btn("ارسال 📩"), Btn("بیخیال ❌")]])


class Private:
    def __init__(self, dp: Dispatcher, db: Database):
        self._id_manager: IdManager = db.id_manager
        self._cache: dict[int, tuple[list[Message], int]] = {}
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(MessageHandler(Filters.chat_type.private, self.on_message))

    def start(self, update: Update, ctx: CallbackContext):
        self._id_manager.add(update.effective_chat.id)

        if ctx.args:
            id = self._id_manager.get(ctx.args[0])
            if id is None:
                update.effective_chat.send_message("متاسفانه کد مورد نظر در سیستم موجود نمیباشد", reply_markup=_home)
                return
            self._cache[update.effective_chat.id] = ([], id)
            update.effective_chat.send_message("لطفا پیام خود را بفرستید", reply_markup=_send)
            return

        update.effective_chat.send_message("سلام، چه کاری میتونم برات انجام بدم؟", reply_markup=_home)

    def on_message(self, update: Update, ctx: CallbackContext):
        code = self._id_manager.add(update.effective_chat.id)
        if update.effective_chat.id not in self._cache.keys():
            if update.message.text == "دریافت لینک پیام ناشناس 🔗":
                update.effective_chat.send_message(f"لینک پیام ناشناس شما:\nhttps://t.me/pmt_testi_bot?start={code}", reply_markup=_home)
                return
            update.effective_chat.send_message(update.message.text, reply_markup=_home)

        if update.message.text == "بیخیال ❌":
            del self._cache[update.effective_chat.id]
            update.effective_chat.send_message("عملیات با موفقیت لغو شد", reply_markup=_home)
            return

        if update.message.text == "ارسال 📩":
            messages, chat = self._cache[update.effective_chat.id]
            if not messages:
                update.effective_chat.send_message("شما هنوز چیزی ارسال نکردید", reply_markup=_send)
                return
            ctx.bot.send_message(chat, "شخصی برای شما پیام فرستاده است:")
            for message in messages:
                message.copy(chat)
            update.effective_chat.send_message("پیام شما با موفقیت ارسال شد", reply_markup=_home)
            return

        self._cache[update.effective_chat.id][0].append(update.message)
