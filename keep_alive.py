from flask import Flask
from threading import Thread

# Flaskアプリ作成
app = Flask('')

# ルートURLにアクセスしたときのレスポンス
@app.route('/')
def home():
    return "I'm alive!"

# Flaskアプリを別スレッドで実行
def run():
    app.run(host='0.0.0.0', port=8080)

# keep_alive関数を呼ぶことでFlaskアプリが起動
def keep_alive():
    t = Thread(target=run)
    t.start()