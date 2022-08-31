import logging
from os.path import dirname, join

from telegram.ext import Updater
from handlers import setup
from utils import Database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Updater("1657050855:AAHs6rfCfmXa7wh2JavolposVpTNmGzPlnE")
db = Database(join(dirname(__file__), "db.json"))

if __name__ == '__main__':
    setup(bot, db)
    bot.start_polling()
    bot.idle()
