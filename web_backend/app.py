# app.py（GPT整形サブスク用Stripe加入ページ）
import stripe
from openai import OpenAI
import json
import os
import random
import string
import uuid
from dotenv import load_dotenv
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for

load_dotenv()

app = Flask(__name__)

stripe.api_key = os.getenv("STRIPE_API_KEY")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

PRICE_ID = "price_1RA7qHHJ0fnIcl70kwCi3EkW"  

@app.route("/write/<id>", methods=["GET", "POST"])
def write_page(id):
    step = int(request.args.get("step", 0))
    file_path = f"formatted_texts/{id}.txt"

    if not os.path.exists(file_path):
        return "ファイルが見つかりません", 404

    with open(file_path, "r", encoding="utf-8") as f:
        paragraphs = [p.strip() for p in f.read().split("\n") if p.strip()]

    if request.method == "POST":
        user_text = request.form.get("written")
        os.makedirs("written_texts", exist_ok=True)
        save_path = f"written_texts/{id}_{step}.txt"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(user_text.strip())

        return redirect(url_for('write_page', id=id, step=step+1))

    if step >= len(paragraphs):
        return "写経おつかれさまでした！🎉", 200

    return render_template("write.html", para=paragraphs[step], step=step, id=id)

@app.route("/upload", methods=["GET", "POST"])
def upload_text():
    if request.method == "GET":
        return render_template("upload.html")

    raw_text = request.form.get("raw_text", "").strip()
    if not raw_text:
        return "文章が空です", 400

    # GPT整形プロンプト
    prompt = f"""以下のテキストを読みやすく整形してください。
--- 以下本文 ---
{raw_text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result_text = response.choices[0].message.content.strip()

    # 保存
    output_id = str(uuid.uuid4())[:8]
    os.makedirs("formatted_texts", exist_ok=True)
    file_path = f"formatted_texts/{output_id}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result_text)

    # リダイレクトして写経開始
    return redirect(url_for("write_page", id=output_id))

@app.route("/format", methods=["POST"])
def format_text():
    data = request.get_json()
    raw_text = data.get("text")

    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    # GPT整形プロンプト
    prompt = f"""読みやすく整形してください。  
各段落は1〜3文程度にまとめ、段落の間には空行（改行2回）を入れてください。

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
    paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

    return jsonify({"paragraphs": paragraphs})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/check/<id>", methods=["POST"])
def check_written_text(id):
    step = int(request.args.get("step", 0))
    user_text = request.form.get("written")

    # 正解の段落を取得
    file_path = f"formatted_texts/{id}.txt"
    if not os.path.exists(file_path):
        return "整形テキストが見つかりません", 404

    with open(file_path, "r", encoding="utf-8") as f:
        paragraphs = [p.strip() for p in f.read().split() if p.strip()]
    
    if step >= len(paragraphs):
        return "段落ステップが範囲外です", 400

    correct = paragraphs[step]

    # GPTに評価させる
    prompt = f"""
以下の2つの文を比較してください。

【元の段落】
{correct}

【写経した文章】
{user_text}

以下の2つの項目を、JSON形式で返してください。

- judgement: "OK", "CLOSE", "NG" のいずれか（意味が通っていればOK、表現が近ければCLOSE）
- comment: 学習者を励ます短いメッセージ（肯定的に）

出力例：
{{
  "judgement": "OK",
  "comment": "素晴らしい出来です！この調子で進んでください。"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    response_text = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(response_text)
        judgement = parsed["judgement"].upper()
        comment = parsed["comment"]
    except Exception:
        # JSONパースに失敗した場合の保険処理
        judgement = "NG"
        comment = "評価に失敗しました。もう一度お願いします。"

    if "OK" in judgement:
        # 合格 → 保存して次へ
        os.makedirs("written_texts", exist_ok=True)
        save_path = f"written_texts/{id}_{step}.txt"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(user_text.strip())

        return redirect(url_for('write_page', id=id, step=step+1))
    else:
        # NG or CLOSE → 再表示、評価付きで
        return render_template("write.html", para=correct, step=step, id=id, result=judgement, comment=comment, prev=user_text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)