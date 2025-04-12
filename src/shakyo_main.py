
from pywinauto.application import Application
import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image
import os
import time
from openai import OpenAI
from dotenv import load_dotenv 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 設定 ===

# Tesseract設定
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ['TESSDATA_PREFIX'] = r"C:\Program Files\Tesseract-OCR\tessdata_best"

# OpenAI APIキー
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# パス設定
OUTPUT_DIR = "../output/shakyo_output_cleaned"
MERGE_PATH = "../output/shakyo_output_gpt/merged_raw_ocr.txt"
FINAL_PATH = "../output/shakyo_output_gpt/merged_pages_1_to_10_final.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FINAL_PATH), exist_ok=True)

# スクリーンショット範囲設定
print("🔍 Kindle ウィンドウを検索中...")
kindle_windows = [w for w in gw.getWindowsWithTitle("Kindle") if "Kindle" in w.title]
if not kindle_windows:
    raise Exception("Kindleウィンドウが見つかりません。Kindleを開いてください。")

win_gw = kindle_windows[0]
if win_gw.isMinimized:
    print("🪟 Kindleウィンドウを復元します")
    win_gw.restore()
    time.sleep(1)

win_gw.maximize()
time.sleep(1)

app = Application(backend="uia").connect(title_re=".*Kindle.*")
win = app.top_window()
win.set_focus()
pyautogui.click(win_gw.left + 100, win_gw.top + 100)
print("✅ Kindle をアクティブ化しました。")

x, y, w, h = win_gw.left, win_gw.top, win_gw.width, win_gw.height
region = (x, y, w, h)

# OCR設定
custom_config = r'--oem 3 --psm 5'
lang = 'jpn_vert'
NUM_PAGES = 10
INTERVAL = 2

# 前処理関数（必要に応じて）
def preprocess_image(pil_image):
    return pil_image

# === OCR + 保存 ===
print("📖 OCRキャプチャ開始...")
for i in range(NUM_PAGES):
    print(f"📸 ページ {i+1} をキャプチャ中...")
    raw_image = pyautogui.screenshot(region=region)
    cleaned_image = preprocess_image(raw_image)

    img_path = os.path.join(OUTPUT_DIR, f"page_{i+1}_cleaned.png")
    cleaned_image.save(img_path)

    text = pytesseract.image_to_string(cleaned_image, lang=lang, config=custom_config)
    txt_path = os.path.join(OUTPUT_DIR, f"page_{i+1}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    pyautogui.press("left")
    time.sleep(INTERVAL)

print("✅ OCR完了")

# === マージ処理 ===
print("📄 OCR結果マージ中...")
merged_text = ""
for i in range(NUM_PAGES):
    txt_path = os.path.join(OUTPUT_DIR, f"page_{i+1}.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            merged_text += f"--- page_{i+1} ---\n{text}\n\n"

with open(MERGE_PATH, "w", encoding="utf-8") as f:
    f.write(merged_text)

print(f"✅ マージ完了: {MERGE_PATH}")

# === GPT整形 ===
print("🤖 GPT整形中（gpt-4）...")

prompt = f"""以下は、OCRとGPTで整形された文章を結合したものです。
内容を変更せず、以下のルールに従って「読みやすく・意味の通る文章」へ整形してください。

【必ず守ってほしいこと】
- 意味が通る箇所の文体・語調・語彙は変更しないこと。
- 文章の内容に対して新たな補完・創作・要約はしないこと。

【許可される修正】
- KindleアプリやOCR由来の意味不明な文字列やUIノイズは削除してください。
  - 例：「x回」「X示奉」「表現」「和島刀」「ロの旅」「[MC]」「和回ーッミニ」など
  - 意味が通らない語句・記号・短文の羅列は全て削除可
- ページまたぎに起因する不自然な接続は調整して構いません（文を繋げたり、区切ったり）
- 漢字＋ふりがな（例：「鍵かぎ」「筏いかだ」）はふりがなを削除し、漢字だけを残してください。

【形式】
- 読みやすい段落構成
- 改行と句読点は自然な形に整えてください

--- 以下本文 ---
{merged_text}
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

with open(FINAL_PATH, "w", encoding="utf-8") as f:
    f.write(response.choices[0].message.content.strip())

print(f"✅ 整形済みテキストを保存しました: {FINAL_PATH}")
