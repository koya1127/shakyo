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

# ルート定義を後から読み込み、上で生成した app に紐付ける
from . import routes  # noqa: E402 – late import to avoid circular reference