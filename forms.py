from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class RegisterForm(FlaskForm):
  username = StringField(
      "ユーザー名",
      validators=[DataRequired(message="ユーザー名は必須です。"), Length(min=2, max=50)],
  )
  email = StringField(
      "メールアドレス",
      validators=[
          DataRequired(message="メールアドレスは必須です。"),
          Email(message="有効なメールアドレスを入力してください。"),
      ],
  )
  password = PasswordField(
      "パスワード",
      validators=[DataRequired(message="パスワードは必須です。"), Length(min=6)],
  )
  submit = SubmitField("ユーザー登録")


class LoginForm(FlaskForm):
  email = StringField(
      "メールアドレス",
      validators=[
          DataRequired(message="メールアドレスは必須です。"),
          Email(message="有効なメールアドレスを入力してください。"),
      ],
  )
  password = PasswordField(
      "パスワード", validators=[DataRequired(message="パスワードは必須です。")]
  )
  submit = SubmitField("ログイン")


class PostForm(FlaskForm):
  image = FileField(
      "画像ファイル",
      validators=[
          FileRequired(message="画像ファイルを選択してください。"),
          FileAllowed(
              ["png", "jpg", "jpeg", "gif"],
              message=(
                  "許可されている形式は png, jpg, jpeg, gif のみです。"
              ),
          ),
      ],
  )
  caption = TextAreaField(
      "キャプション", validators=[Length(max=500, message="500文字以内で入力してください。")]
  )
  submit = SubmitField("投稿する")
