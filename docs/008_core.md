# 008_core.md

## コア機能の処理フロー

1. ローカルでOCR → マージ
2. Webサーバーにテキスト送信（/format）
3. GPT-4で整形
4. 整形済み文章を `formatted_texts/<id>.txt` に保存
5. IDを返す
6. ユーザーは `/text/<id>` を通じて写経体験へ
7. ユーザーが写経内容を入力し、サーバーに送信（/write/<id> POST）
8. `written_texts/<id>_<step>.txt` に保存される
9. サーバーは GPT-4 へ写経内容を送信し、判定（OK / CLOSE / NG）と励ましコメントを取得
10. GPTは OK / CLOSE / NG の判定とコメントを返す。OKは保存して次の段落へ遷移。評価コメントは次の画面に引き継いで表示。CLOSE、NG の場合は再入力を促す。将来的にはCLOSEでも進むようにしたい
11. `/progress/<user_id>` で進捗一覧が確認可能