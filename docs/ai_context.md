# ai_context.md - アプリケーション全体コンテキスト

## 1. アプリの概要
友人同士で旅行や日常の写真をシェアし合う、インスタグラム風の写真共有Webアプリケーションです。

## 2. 技術スタック
- **言語**: Python
- **Webフレームワーク**: Flask
- **ORM / データベース**: Peewee / SQLite (`app.db`)
- **認証**: Flask-Login
- **フォーム・バリデーション**: Flask-WTF, WTForms, email-validator
- **セキュリティ・ユーティリティ**: Werkzeug (パスワードハッシュ、ファイル名サニタイズ), python-dotenv
- **フロントエンド・デザイン**: ローカル管理のBootstrap / CSS

## 3. データベース構造
- **User（ユーザー）テーブル**: `id`, `username` (Unique), `email` (Unique), `password`
- **Post（投稿）テーブル**: `id`, `user` (FK -> User), `image_filename`, `caption` (Nullable), `created_at` (DateTimeField)
- **Like（いいね）テーブル**: `id`, `user` (FK -> User), `post` (FK -> Post) ※(user, post)の複合ユニーク制約

## 4. ルーティング設計
- `GET /` : 投稿一覧（タイムライン）
- `GET, POST /register` : ユーザー登録
- `GET, POST /login` : ログイン
- `GET /logout` : ログアウト
- `GET, POST /posts/new` : 投稿作成（**要ログイン**・プロジェクト直下の `uploads/` へ画像保存）
- `GET /posts/<int:post_id>` : 投稿詳細画面
- `POST /posts/<int:post_id>/like` : いいね非同期更新（**要ログイン**・JSON返却）
