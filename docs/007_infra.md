# 007_infra.md

## インフラ構成図（開発中）

[ローカルPC]
└── shakyo_main.py
    ├─ Kindleを自動アクティブ化
    ├─ スクリーンキャプチャ + OCR
    └─ マージ済みテキストをサーバーにPOST（/format）

     ↓ POST

[Webサーバー（Flask）]
└── app.py
    ├─ /format（GPT整形 → 保存）
    ├─ /text/<id>（整形済みテキストの取得）
    └─ formatted_texts/<id>.txt に保存

     ↓ APIで取得

[Web UI（将来構築）]
└── チャット形式の写経ビュー
    ├─ 1段落ずつ提示
    ├─ 「次へ」「メモ」「わからない」等
    └─ GPT応援コメント or 解説

---

## ディレクトリ構成（2025年4月時点）

📂 実行ディレクトリのルート：  
`C:\Users\fab24\Documents\shakyo`

shakyo/
├─ docs/                          # この仕様書ファイルたち（.md）
│   ├─ 000_overview.md
│   ├─ 001_pages.md
│   └─ ...（〜010）
│
├─ src/                           # ローカルOCR処理（クライアント側）
│   └─ shakyo_main.py
├─ web_backend/                   # Flaskサーバー側
│   ├─ app.py                     # APIルーティング
│   ├─ formatted_texts/          # GPT整形結果（.txt保存）
│   ├─ written_texts/            # 写経内容保存 
│   └─ templates/                # HTMLテンプレート
│       └─ write.html            # チャット形式ビュー 
├─ .gitignore
├─ README.md
└─ requirements.txt（←依存管理しておくと吉）

---

## 補足

- GPT APIキーは **Flaskサーバー側のみ保持**
- ローカルは OCR結果をPOSTするだけ
- - `/text/<id>` を通じて整形結果を段落表示するAPIは実装済み
- 最終的には「Next.js + API連携」で写経ビューを提供予定
- GPTに写経内容を送信し、段落ごとに OK / CLOSE / NG の判定を受け取る機能を実装済み
- NG の場合のみ、その場で評価＋励ましコメントを表示し、再入力を促す仕様
