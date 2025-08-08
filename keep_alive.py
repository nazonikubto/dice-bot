# keep_alive.py

from flask import Flask
from threading import Thread
from bot import start_bot  # bot.py に定義された起動関数

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running via gunicorn!"

# サーバー起動時に Discord Bot を別スレッドで起動
Thread(target=start_bot).start()






