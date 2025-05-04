# routes.py
import uuid
from flask import Blueprint, request, redirect, url_for, render_template 
from openai import OpenAI
from pathlib import Path 

client = OpenAI()   

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_text():
    if request.method == "GET":
        return render_template("upload.html")

    raw_text = request.form.get("raw_text", "").strip()
    if not raw_text:
        return "文章が空です", 400

    # GPT 整形プロンプト（元コードをそのまま）
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

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    result_text = response.choices[0].message.content.strip()

    # 保存
    output_id = uuid.uuid4().hex[:8]
    Path("formatted_texts").mkdir(exist_ok=True)
    Path(f"formatted_texts/{output_id}.txt").write_text(result_text, encoding="utf-8")

    return redirect(url_for("write.write_page", id=output_id))
