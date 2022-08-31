from telegram.ext import Updater
from utils import Database
from .private import Private
from .group import Group


def setup(bot: Updater, db: Database):
    dp = bot.dispatcher
    Private(dp, db)
    Group(dp, db)
