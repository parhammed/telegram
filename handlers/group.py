from re import compile

from telegram.ext import Dispatcher, CallbackContext, MessageHandler, Filters
from telegram import Update, User, TelegramError

from utils import Database

cmd_re = compile(r"-(?P<cmd>\S+)( (?P<arg>\S+))?")


class Group:
    def __init__(self, dp: Dispatcher, db: Database):
        self._db = db
        dp.add_handler(MessageHandler(Filters.chat_type.groups, self.on_message))

    def on_message(self, update: Update, ctx: CallbackContext):
        match = cmd_re.match(update.message.text)
        if match is None:
            return
        cmd, arg = match.group("cmd"), match.group("arg")
        if arg is not None and arg.isnumeric():
            arg = int(arg)
        Id = arg or update.message.reply_to_message.from_user.id
        if not Id:
            update.message.reply_text("کاربر مورد نظر شما یافت نشد")
            return

        if cmd == "اخراج":
            try:
                update.effective_chat.ban_member(Id, until_date=0)
            except TelegramError:
                update.message.reply_text("کاربر مورد نظر شما یافت نشد")
            else:
                update.message.reply_text("کاربر مورد نظر شما با موفقیت اخراج شد")

        elif cmd == "بن":
            try:
                update.effective_chat.ban_member(Id)
            except TelegramError:
                update.message.reply_text("کاربر مورد نظر شما یافت نشد")
            else:
                update.message.reply_text("کاربر مورد نظر شما با موفقیت اخراج شد")

        elif cmd in ("انبن", "آنبن"):
            try:
                update.effective_chat.unban_member(Id, only_if_banned=True)
            except TelegramError:
                update.message.reply_text("کاربر مورد نظر شما یافت نشد")
            else:
                update.message.reply_text("کاربر مورد نظر شما با موفقیت اخراج شد")

        if cmd == "اخطار":
            try:
                member = update.effective_chat.get_member(Id)
            except TelegramError:
                update.message.reply_text("کاربر مورد نظر شما یافت نشد")
                return
            d = str(member.user.id)
            x = self._db.setdefault(d, 0)
            x += 1
            self._db[d] = x
            self._db.save()
            mention = f"@{member.user.username}" if member.user.username else f"[{member.user.full_name}](tg://user?id={d})"
            update.message.reply_text(f"کاربر {mention} با موفقیت یک وارن دریافت کرد\nتعداد وارن های در حال حاضر این کاربر:{x}")

        # پاکسازی اخطار ها
        if cmd == "پاک":
            try:
                member = update.effective_chat.get_member(Id)
            except TelegramError:
                update.message.reply_text("کاربر مورد نظر شما یافت نشد")
                return
            d = str(member.user.id)
            self._db.pop(d, None)
            self._db.save()
            mention = f"@{member.user.username}" if member.user.username else f"[{member.user.full_name}](tg://user?id={d})"
            update.message.reply_text(f"تمامیه وارن های {mention} حذف شدند")


