# coding_rules.md - コーディング規約と実装ルール

## 1. データベース接続管理 (ライフサイクル)
- Flaskのリクエスト処理において、接続の開きっぱなしや閉じ忘れを防ぐため、以下のフックを必ず実装する。
  ```python
  @app.before_request
  def before_request():
      db.connect()

  @app.teardown_request
  def teardown_request(exc):
      if not db.is_closed():
          db.close()
          