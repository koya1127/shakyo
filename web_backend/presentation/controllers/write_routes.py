# web_backend/presentation/controllers/write_routes.py
from flask import Blueprint, request, render_template, redirect, url_for
import uuid, os, json, random, string
from pathlib import Path
from openai import OpenAI
from web_backend.utils.paragraph import split_paragraphs

client = OpenAI()

write_bp = Blueprint("write", __name__)

@write_bp.route("/write/<id>", methods=["GET", "POST"])
def write_page(id):
    
    step = int(request.args.get("step", 0))
    file_path = f"formatted_texts/{id}.txt"
    prev_result = request.args.get("prev_result")
    prev_comment = request.args.get("prev_comment")

    if not os.path.exists(file_path):
        return "ファイルが見つかりません", 404

    with open(file_path, "r", encoding="utf-8") as f:
        paragraphs = paragraphs = split_paragraphs(f.read())

    if request.method == "POST":
        user_text = request.form.get("written")
        os.makedirs("written_texts", exist_ok=True)
        save_path = f"written_texts/{id}_{step}.txt"
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(user_text.strip())

        return redirect(url_for('write_page', id=id, step=step+1))

    if step >= len(paragraphs):
        return "写経おつかれさまでした！🎉", 200
    
    user = request.args.get("user")  

    return render_template("write.html", para=paragraphs[step], step=step, id=id, result=prev_result, comment=prev_comment, user=user) 