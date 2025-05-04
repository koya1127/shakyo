# 003_structure.md

## 構成

### ローカル（クライアント）
- `shakyo_main.py`：OCRキャプチャ、ページマージ、整形APIへPOST

### Webサーバー（Flask）
- `app.py`：
  - `/format`：GPT整形＆保存
  - `/webhook`：Stripeトークン処理
  - `/text/<id>`：整形文取得API 
  - `/write/<id>`：1段落ずつ写経・保存フォーム 
  - `/check/<id>`：GPTによる段落判定API（POST）

#### 共通ヘルパ
- `utils/paragraph.py`：段落を空行で分割する純粋関数 `split_paragraphs()`

### フロントエンド（予定）
- チャットUI
- progress表示・記録

### 保存形式
- 整形結果：`formatted_texts/<id>.txt`
- 写経内容：`written_texts/<id>_<step>.txt`

