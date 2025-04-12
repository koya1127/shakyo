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


### フロントエンド（予定）
- チャットUI
- progress表示・記録

### 保存形式
- `formatted_texts/<id>.txt`（段落ごとに保存可能にする）
