# GPT整形 × 写経継続支援システム

## 1. 目的とスコープ

このドキュメントは本プロジェクトの **設計方針・コード規約・コメント指針** を一元管理し、実装・レビュー・オンボーディングを円滑にすることを目的とする。

---

## 2. 設計指針

| 目標      | 採用方針                                                |
| ------- | --------------------------------------------------- |
| **可読性** | 小規模ながらもレイヤ分離を徹底し、役割が近いものを近接配置する                     |
| **拡張性** | 将来的な Next.js / Redis / Stripe 拡張を想定し、疎結合インターフェースを設計 |
| **保守性** | テスト容易性を重視し、副作用を Infrastructure 層に隔離                 |

### 2.1 アーキテクチャ概要（Clean Architecture Lite）

```
app/                    # Presentation (Flask routes / Templates)
├─ controllers/         # ルーティング + 入出力バリデーション
├─ services/            # Application 層（ユースケース）
├─ domain/              # エンティティ・値オブジェクト・リポジトリIF
├─ infrastructure/      # DB / Stripe / GPT 外部依存の具象実装
└─ utils/               # 共通ヘルパ
```

> **NOTE**: DDD の “集約” はオーバースペックになり得るため、 ドメインロジックが肥大化し始めた段階で見直す。

### 2.2 ディレクトリ詳細

- **controllers/**: Flask Blueprint。I/O 変換のみ。
- **services/**: ビジネスユースケース (`WriteParagraph`, `CheckProgress`) を 1 クラス 1 関数で表現。
- **domain/**
  - `entities.py`: `Text`, `Paragraph`, `UserProgress`
  - `repositories.py`: 抽象 `ProgressRepository` / `TextRepository`
- **infrastructure/**
  - `sqlite_progress.py`: `ProgressRepository` 実装
  - `gpt_client.py`: GPT 呼び出しラッパー
  - `stripe_client.py`: Stripe ラッパー
- **utils/**: `load_paragraphs`, `gpt_format` など純粋関数群。

---

## 3. コメント & Docstring 規約

### 3.1 Docstring 形式（Google Style）

```python
def gpt_format(text: str) -> str:
    """GPT-4 で文章を整形して返すユーティリティ。

    Args:
        text: OCR 取得した生テキスト。

    Returns:
        GPT 整形後のテキスト（段落区切り \n 含む）。
    """
```

- **モジュール先頭**: 簡潔な概要 + 依存関係。
- **クラス**: 目的・主要属性・使用例 (`Example:`) を記述。

### 3.2 インラインコメント

| 用途           | 書式例                                |
| ------------ | ---------------------------------- |
| **アルゴリズム補足** | `# Levenshtein < 3 のとき GPT スキップ`   |
| **TODO**     | `# TODO(koya): Redis キューに置き換え`     |
| **FIXME**    | `# FIXME: 並列書込で稀に JSONDecodeError` |

### 3.3 禁則事項

- コメントでコードを上書きする長文手順書 → `docs/` に移動。
- 日本語 & 英語混在可。ただしファイル単位で統一。

---

## 4. ドキュメント運用

1. 変更が発生したら **本ファイルを Pull Request 内で更新**。
2. “設計/規約に影響する変更” は PR テンプレ `architecture_change` を使用。

---

## 5. 将来ロードマップ（抜粋）

| フェーズ   | 対応項目                                    |
| ------ | --------------------------------------- |
| Phase1 | SQLite 化 / utils 切り出し / Lock ガード（*進行中*） |
| Phase2 | controllers/ services/ への分割、Blueprint 化 |
| Phase3 | Redis + RQ / Stripe 本番化、Next.js フロント移行  |

---

**Last Update:** 2025-04-29



## 3. 現在のディレクトリ構成（Box 作成後）

```
web_backend/
├── presentation/          # 受付カウンター (Flask ルート)
│   ├─ __init__.py
│   └─ routes.py
├── application/           # ユースケース
│   └─ __init__.py
├── domain/                # ビジネスロジック
│   └─ __init__.py
├── infrastructure/        # 外部依存
│   └─ __init__.py
└── templates/             # HTML
```

---

## 4. コメント / Docstring 規約

> **目的** : “何をするコードか” を 3 秒で把握できるようにする。

### 4.1 モジュール / パッケージ (`__init__.py`)

```python
"""Presentation 層: Flask アプリ生成窓口。

外部から Flask を直接 import させないため、このモジュールで
app を 1 回だけ生成し、routes を読み込んで紐付ける。"""
```

- 1 行目 = 概要（50 文字以内）
- 2 行目空行 + 詳細 (箇条書き可)

### 4.2 関数・メソッド (Google Docstring)

```python
def calc_score(text: str) -> int:
    """テキスト長 ×10 のスコアを返す。

    Args:
        text: 入力文字列。

    Returns:
        int: スコア値。
    """
```

- 引数・戻り値を明示。外部副作用があれば **Raises:** で列挙。

### 4.3 インラインコメント

- 行末コメントは 60–70 桁で改行。
- 「何をしているか」より **“なぜ”** を書く。

```python
app = Flask(__name__)  # ここで 1 回だけ生成し他層と共有
```

---

> **運用** : 新規ファイル追加時は Docstring を必ず書く。既存関数を修正したら影響する Args/Returns を更新。
