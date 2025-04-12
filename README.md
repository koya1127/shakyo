
# 写経OCRアプリ

## 概要
Kindleアプリで表示中の縦書き日本語テキストを自動でキャプチャし、OCR（Tesseract）でテキスト化。その後、GPTを使って自然な文章へと整形し、写経に適した形式で出力します。

- 自動キャプチャ
- 高精度な縦書きOCR（Tesseract + jpn_vert）
- GPTによる整形支援
- ユーザー操作最小限

---

## フォルダ構成

```
shakyo/
├── src/
│   ├── shakyo_main.py        # ← 実行ファイル
│   └── old_versions/         # ← 過去スクリプトの保管場所
├── output/                   # ← 出力ファイル（Git対象外）
│   ├── shakyo_output_raw/        # 生スクショ＋OCR結果
│   ├── shakyo_output_cleaned/    # 前処理画像＋OCR結果
│   └── shakyo_output_gpt/        # GPT整形済みテキスト
├── .gitignore
└── README.md
```

---

## 使用方法

### 1. 実行環境

- Windows（Kindleアプリ使用）
- Python 3.10+
- OpenAI APIキー（GPT整形用）

### 2. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

※ `requirements.txt` は以下の内容：
```text
openai
pytesseract
pyautogui
pygetwindow
pywinauto
opencv-python
numpy
Pillow
```

### 3. OCR設定

- Tesseractインストール済み（`C:\Program Files\Tesseract-OCR\`）
- `tessdata_best/jpn_vert.traineddata` を配置済み

### 4. 実行方法

```bash
cd src/
python shakyo_main.py
```

---

## 出力例

- `output/shakyo_output_gpt/page_1_gpt.txt` に整形済みの文章が保存されます。

---

## 補足

- OCR精度が低い場合は `shakyo_output_cleaned/` の画像を見直すことで原因特定が可能です。
- GPT整形精度が不十分な場合は `model="gpt-4"` → `"gpt-3.5-turbo"` に切り替えて負荷調整も可能です。

---

## 今後の予定（ToDo）

- [ ] PDF出力機能の追加
- [ ] 写経UI（WebまたはCLI）の構築
- [ ] GPTによる語句注釈オプション

---

## ライセンス
MIT License
