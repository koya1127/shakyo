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
├─ web_backend/                   # サーバー側（Flask 基盤）
│   ├─ presentation/              # 受付カウンター：HTTP ルート
│   │   ├─ __init__.py
│   │   └─ routes.py              # ※旧 app.py を移動予定
│   │
│   ├─ application/               # ユースケース：手順書
│   │   └─ __init__.py
│   │
│   ├─ domain/                    # ビジネスロジック：段落比較など
│   │   └─ __init__.py
│   │
│   ├─ infrastructure/            # 外部サービス接続
│   │   ├─ __init__.py
│   │   └─ openai_client.py  など
│   │
│   ├─ templates/                 # HTML テンプレート
│   │   ├─ upload.html
│   │   └─ write.html
│   │
│   └─ utils/                     # 共通ヘルパー（必要あれば）
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

## Git / GitHub運用（2025年4月）

- `.env` を用いたAPIキー管理を採用し、`.gitignore` で追跡除外済み
- GitHub上の履歴には一切のAPIキーが含まれないよう、orphanブランチによる履歴リセット＋再構築済み
- GitHub連携済みリポジトリ：`https://github.com/koya1127/shakyo`
- RenderにてGitHub連携デプロイを使用（push → 自動デプロイ or 手動Deploy）
- デプロイ用の `requirements.txt` は最小構成に手動で編集
- push前に `git commit --amend` などを活用し、誤った履歴が含まれないよう管理

