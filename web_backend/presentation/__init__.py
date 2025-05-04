# presentation/__init__.py
"""
Presentation 層: Flask アプリを 1 回だけ生成して公開するモジュール。

- 他層は ``from presentation import app`` で Flask 依存を間接利用する。
- ここで ``routes`` を読み込むことで、アプリ生成直後に URL ルールを登録する。
"""
from dotenv import load_dotenv
load_dotenv()   

from flask import Flask
app = Flask(__name__)  # アプリ本体（シングルトン）

# ───────── Blueprints ─────────
from .controllers.upload_routes import upload_bp # /upload 画面と整形処理
from .controllers.write_routes import write_bp # /write/<id> 写経入力フォーム
from .controllers.check_routes import check_bp # /check/<id> GPT 判定API
app.register_blueprint(upload_bp)
app.register_blueprint(write_bp)
app.register_blueprint(check_bp)

# ルート定義を後から読み込み、上で生成した app に紐付ける
from . import routes  # E402: 循環 import を避けるため late import