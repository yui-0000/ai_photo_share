import os
from datetime import datetime
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    PrimaryKeyField,
    SqliteDatabase,
    TextField,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from forms import LoginForm, PostForm, RegisterForm

# データベースの初期化 (SQLite)
db = SqliteDatabase("app.db")

# 画像の保存先ディレクトリ（プロジェクト直下の uploads/posts/）
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "posts")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class BaseModel(Model):

    class Meta:
        database = db


# ユーザーモデル
class User(BaseModel, UserMixin):
    id = PrimaryKeyField()
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()


# 投稿モデル
class Post(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref="posts")
    image_filename = CharField()
    caption = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)


app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-for-development"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# 最大ファイルサイズの制限（例: 16MB）
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Flask-Login の初期設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id == user_id)


# データベース接続管理
@app.before_request
def before_request():
    db.connect()


@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()


@app.route("/")
def index():
    db.create_tables([User, Post], safe=True)
    # 新着順で投稿一覧を取得
    posts = Post.select().order_by(Post.created_at.desc())
    return render_template("index.html", posts=posts)


# 画像配信ルート（uploads/posts/ 内のファイルにアクセスするため）
@app.route("/uploads/posts/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.get_or_none(User.email == form.email.data):
            flash("このメールアドレスは既に登録されています。", "danger")
            return render_template("register.html", form=form)

        if User.get_or_none(User.username == form.username.data):
            flash("このユーザー名は既に使用されています。", "danger")
            return render_template("register.html", form=form)

        hashed_password = generate_password_hash(form.password.data)
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
        )
        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_or_none(User.email == form.email.data)
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("ログインしました。", "success")
            return redirect(url_for("index"))
        else:
            flash("メールアドレスまたはパスワードが間違っています。", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("index"))


# 新規投稿ルート（ログイン必須）
@app.route("/posts/new", methods=["GET", "POST"])
@login_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        f = form.image.data
        # 安全なファイル名に変換
        filename = secure_filename(f.filename)
        # 同名ファイル衝突を防ぐため、プレフィックスにタイムスタンプを付与
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"

        # uploads/posts/ に保存
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        f.save(file_path)

        # データベースに保存
        Post.create(
            user=current_user,
            image_filename=unique_filename,
            caption=form.caption.data,
        )
        flash("写真を投稿しました！", "success")
        return redirect(url_for("index"))

    return render_template("post_new.html", form=form)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
