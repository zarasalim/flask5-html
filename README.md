# flask5-html


APP.PY

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




LOGIN.HTML


<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Логин</title>
</head>
<body>

    <h1>Вход</h1>

    <form method="POST">

        <label>Логин:</label>
        <input type="text" name="username" required>

        <br><br>

        <label>Пароль:</label>
        <input type="password" name="password" required>

        <br><br>

        <button type="submit">Войти</button>

    </form>

    <br>

    <a href="{{ url_for('register') }}">Регистрация</a>

</body>
</html>



REGISTER.HTML


<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Регистрация</title>
</head>
<body>

    <h1>Регистрация</h1>

    <form method="POST">

        <label>Логин:</label>
        <input type="text" name="username" required>

        <br><br>

        <label>Email:</label>
        <input type="email" name="email" required>

        <br><br>

        <label>Пароль:</label>
        <input type="password" name="password" required>

        <br><br>

        <button type="submit">Зарегистрироваться</button>

    </form>

    <br>

    <a href="{{ url_for('login') }}">Уже есть аккаунт?</a>

</body>
</html>


HOME.HTML


<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Главная</title>
</head>
<body>

    <h1>Персональный блог</h1>

    <a href="{{ url_for('register') }}">
        <button>Регистрация</button>
    </a>

    <a href="{{ url_for('login') }}">
        <button>Логин</button>
    </a>

</body>
</html>



INDEX.HTML


<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{% block title %}Мой блог{% endblock %}</title>

    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>

<body>

    <header>
        <h1>Мой блог программиста</h1>

        <nav>
            <a href="/">Главная</a>
            <a href="/notes">Дневник программиста</a>
        </nav>
    </header>

    <main>
        {% block content %}

        <h2>Добро пожаловать!</h2>

        <p>
            Это мой учебный блог по программированию.
        </p>

        {% endblock %}
    </main>

    <footer>
        <p>Учебный проект Flask + Jinja2</p>
    </footer>

</body>
</html>


NOTES.HTML


{% extends "index.html" %}

{% block title %}
Дневник программиста
{% endblock %}

{% block content %}

<h2>Дневник программиста</h2>

<section class="form-section">

    <h3>Добавить новую запись</h3>

    <form method="POST">

        <label for="title">Заголовок записи:</label>

        <input
            type="text"
            id="title"
            name="title"
            required
        >

        <label for="text">Текст записи:</label>

        <textarea
            id="text"
            name="text"
            rows="6"
            required
        ></textarea>

        <button type="submit">
            Добавить запись
        </button>

    </form>

</section>


<section class="notes-section">

    <h3>Мои записи</h3>

    {% if notes %}

        {% for note in notes %}

            <article class="note">

                <h3>{{ note.title }}</h3>

                <p>{{ note.text }}</p>

            </article>

        {% endfor %}

    {% else %}

        <p>Пока нет ни одной записи.</p>

    {% endif %}

</section>

{% endblock %}


STYLE.CSS


* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #f2f2f2;
    color: #333;
}

header {
    background-color: #222;
    color: white;
    padding: 25px;
    text-align: center;
}

header h1 {
    margin: 0 0 20px;
}

nav a {
    color: white;
    text-decoration: none;
    margin: 0 10px;
}

nav a:hover {
    text-decoration: underline;
}

main {
    max-width: 900px;
    margin: 30px auto;
    padding: 30px;
    background-color: white;
    border-radius: 10px;
}

h2 {
    color: #333;
}

.form-section {
    margin-bottom: 40px;
}

form {
    display: flex;
    flex-direction: column;
}

label {
    margin-top: 15px;
    margin-bottom: 5px;
    font-weight: bold;
}

input,
textarea {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 16px;
}

button {
    margin-top: 20px;
    padding: 12px;
    border: none;
    border-radius: 5px;
    background-color: #333;
    color: white;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background-color: #555;
}

.note {
    margin-top: 20px;
    padding: 20px;
    background-color: #f5f5f5;
    border-left: 5px solid #333;
    border-radius: 5px;
}

.note h3 {
    margin-top: 0;
}

footer {
    text-align: center;
    padding: 20px;
    color: #777;
}


MODELS.PY


from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.Text, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
