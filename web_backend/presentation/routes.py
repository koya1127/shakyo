# routes.py
import stripe
from openai import OpenAI
import json
import os
import random
import string
import uuid
from flask import request, jsonify, render_template, redirect, url_for
from . import app 
from web_backend.utils.paragraph import split_paragraphs


stripe.api_key = os.getenv("STRIPE_API_KEY")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

PRICE_ID = "price_1RA7qHHJ0fnIcl70kwCi3EkW"  

@app.route("/format", methods=["POST"])
def format_text():
    data = request.get_json()
    raw_text = data.get("text")

    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    # GPT整形プロンプト
    prompt = f"""以下の文章を読みやすく整形してください。

【絶対に守ること】
- 意味や内容は一切変更しないでください。
- 文の語順や語句の言い換えは絶対に行わないでください。
- 改行位置と空白の調整のみ許可します。
- 誤字・脱字がある場合も修正しないでください。

【形式】
- おおよそ100文字ごとに段落を分けてください（空行で区切ってください）。
- 各段落内では、不自然な改行を除去して構いません。

--- 以下本文 ---
{raw_text}
"""

    # OpenAI呼び出し
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result_text = response.choices[0].message.content.strip()

    # ファイル保存（ID付き）
    output_id = str(uuid.uuid4())[:8]
    os.makedirs("formatted_texts", exist_ok=True)
    file_path = f"formatted_texts/{output_id}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    print(f"✅ 整形結果を保存しました: {file_path}")
    return jsonify({"id": output_id})

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': PRICE_ID,
                'quantity': 1,
            }],
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )
        return jsonify({"url": checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 400
    
@app.route("/progress/<user_id>")
def show_progress(user_id):
    try:
        with open("user_progress.json", "r", encoding="utf-8") as f:
            progress = json.load(f)
    except FileNotFoundError:
        return f"ユーザー {user_id} の進捗データはまだありません。", 200

    if user_id not in progress:
        return f"ユーザー {user_id} の進捗は見つかりません。", 200

    user_data = progress[user_id]

    html = f"<h2>🗂 ユーザー {user_id} の進捗状況</h2><ul>"
    for text_id, step in user_data.items():
        url = f"/write/{text_id}?step={step}&user={user_id}"
        html += f"<li>📘 テキストID: <code>{text_id}</code> → {step}段落まで完了！ <a href='{url}'>続きから▶</a></li>"
    html += "</ul>"

    return html, 200


@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    print("📩 Webhook受信！")
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    except Exception as e:
        print("Webhook error:", e)
        return str(e), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        email = session.get("customer_email")

        print("✅ ユーザーがサブスク加入した！")
        print("顧客ID:", customer_id)
        print("メール:", email)

        # 8文字のトークンを発行（英数字ランダム）
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        print("🔑 発行トークン:", token)

        # 保存用パス
        user_data_path = "user_data.json"

        # 既存のデータを読み込む
        if os.path.exists(user_data_path):
            with open(user_data_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
        else:
            user_data = {}

        # 顧客IDを保存（上書き or 新規）
        user_data[customer_id] = {
            "email": email,
            "token": token,
            "allowed": True
        }

        # 保存
        with open(user_data_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

        print(f"💾 顧客 {customer_id} を user_data.json に保存しました！")
    
    return "OK", 200

@app.route("/text/<id>", methods=["GET"])
def get_formatted_text(id):
    file_path = f"formatted_texts/{id}.txt"
    
    if not os.path.exists(file_path):
        return jsonify({"error": "not found"}), 404

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 空行で段落分割し、空でない行だけ返す
    paragraphs = split_paragraphs(content)

    return jsonify({"paragraphs": paragraphs})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


