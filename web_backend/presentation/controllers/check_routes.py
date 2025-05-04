# web_backend/presentation/controllers/check_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, render_template
import os, json, uuid
from openai import OpenAI
from web_backend.utils.paragraph import split_paragraphs


client = OpenAI()

check_bp = Blueprint("check", __name__)

@check_bp.route("/check/<id>", methods=["POST"])
def check_written_text(id):
    step = int(request.args.get("step", 0))
    user_text = request.form.get("written")
    user_id = request.args.get("user")

    # 正解の段落を取得
    file_path = f"formatted_texts/{id}.txt"
    if not os.path.exists(file_path):
        return "整形テキストが見つかりません", 404

    with open(file_path, "r", encoding="utf-8") as f:
        paragraphs = split_paragraphs(f.read())
    
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
- comment: 学習者を励ます、**感情のこもった応援コメント**を返してください。
  - 特に、元の段落の**内容・雰囲気・テーマ**を踏まえたコメントにしてください。
  - 「どういう意味のある段落か」「写経元の文の特徴」など、写経元の文や解釈を含めてください。
  - 書き写した本人に「ちゃんと伝わってるよ」と感じさせるコメントを、肯定的な言葉で表現してください。

出力形式（例）：
{{
  "judgement": "OK",
  "comment": "（ここに応援コメント）"
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

        # ✅ 進捗ログを user_progress.json に記録
        user_id = request.args.get("user")
        if user_id:
            try:
                with open("user_progress.json", "r", encoding="utf-8") as f:
                    progress = json.load(f)
            except FileNotFoundError:
                progress = {}

            progress.setdefault(user_id, {})[id] = step + 1

            with open("user_progress.json", "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)

        # ✅ 次の段落へ（評価コメント付きで表示）
        return redirect(url_for("write.write_page", id=id, step=step+1,
                        user=user_id,
                        prev_result=judgement, prev_comment=comment))

    else:
        # NG or CLOSE → 再表示、評価付きで
        return render_template("write.html", para=correct, step=step, id=id, result=judgement, comment=comment, prev=user_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)