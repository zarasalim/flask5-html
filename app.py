from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Notes, Users


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = "my-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]


db.init_app(app)

migrate = Migrate(app, db)

jwt = JWTManager(app)


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/notes", methods=["GET", "POST"])
def notes_page():

    if request.method == "POST":

        title = request.form["title"]
        text = request.form["text"]

        new_note = Notes(
            title=title,
            text=text
        )

        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for("notes_page"))

    notes = Notes.query.all()

    return render_template(
        "notes.html",
        notes=notes
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = Users.query.filter_by(username=username).first()

        if existing_user:
            return "Такой пользователь уже существует"

        hashed_password = generate_password_hash(password)

        user = Users(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            token = create_access_token(
                identity=str(user.id)
            )

            response = redirect(url_for("notes_page"))

            response.set_cookie(
                "access_token",
                token,
                httponly=True
            )

            return response

        return "Неверный логин или пароль"

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
