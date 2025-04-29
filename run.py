# run.py  

"""
ローカル用の起動スクリプト。
presentation パッケージで生成された Flask アプリ (app) を読み込み、
デバッグサーバーを立ち上げるだけ。
"""

from web_backend.presentation import app  

if __name__ == "__main__":
    # ポートはお好みで。debug=True なら自動リロードが効きます
    app.run(host="0.0.0.0", port=5000, debug=True)
