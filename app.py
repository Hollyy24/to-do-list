from flask import Flask, redirect, render_template, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from flask_bootstrap import Bootstrap
from form import RegisterForm, ListForm, LoginForm
import os
app = Flask(__name__)
Bootstrap(app)



app.config["SECRET_KEY"] = os.getenv('DB_KEY')


login_manager = LoginManager()
login_manager.init_app(app)




@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI",'sqlite:///user.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)

    todo_lists: Mapped[list["TodoList"]] = relationship("TodoList", back_populates="user")
    

class TodoList(db.Model):
    __tablename__ = "to_do_lists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="todo_lists")


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("home_page.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    register = RegisterForm()
    if register.is_submitted():
        password = generate_password_hash(
            register.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=register.name.data,
            password=password,
            email=register.email.data,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("edit_list"))
    return render_template("register.html", register=register, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        email = login.email.data
        password = login.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("edit_list"))
        flash("We can't fin your account!")
    return render_template("log_in.html", login=login, logged_in=current_user.is_authenticated)


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit_list():
    list = ListForm()
    todos = current_user.todo_lists
    if list.validate_on_submit():
        new_list = TodoList(
            context=list.context.data,
            user_id=current_user.id,
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for('edit_list'))
    return render_template("edit_list.html", todos=todos, list=list, logged_in=current_user.is_authenticated)


@app.route("/delete/<string:todo_id>", methods=["POST"])
@login_required
def delete_list(todo_id):
    todo = TodoList.query.get(todo_id)
    if todo and todo.user_id == current_user.id:
        db.session.delete(todo)
        db.session.commit()
        flash("Todo deleted successfully", "success")
        return redirect(url_for('edit_list'))


@app.route("/logout")
@login_required
def log_out():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
