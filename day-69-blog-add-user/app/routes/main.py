from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
from app.models import BlogPost, User, Comment
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegisterForm, AddPostForm, CommentForm
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

# Home page -> show all posts
@main.route('/')
def index():
    all_posts = BlogPost.query.order_by(BlogPost.date.desc()).all()
    return render_template("index.html", all_posts=all_posts, current_user=current_user)


# Show all posts page
@main.route('/posts')
def get_all_posts():
    all_posts = BlogPost.query.order_by(BlogPost.date.desc()).all()
    return render_template("index.html", all_posts=all_posts, current_user=current_user)


@main.route("/post/<int:post_id>", methods=["GET", "POST"])
def get_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            text=form.comment_text.data,
            author_id=current_user.id,
            post_id=post.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Your comment was added!", "success")
        return redirect(url_for("main.get_post", post_id=post.id))
    return render_template("post.html", post=post, form=form, current_user=current_user)

@main.route('/add-post', methods=["GET", "POST"])
@login_required
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title_subtitle=f"{form.title.data} - {form.subtitle.data}",
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user  # Uses relationship from models.py
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Your blog post has been published!", "success")
        return redirect(url_for("main.get_all_posts"))

    return render_template("add_post.html", form=form, current_user=current_user)

# Register new user
@main.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user email already exists
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('main.login'))

        # Hash password
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Create new user
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        # Auto login after register
        login_user(new_user)
        return redirect(url_for("main.get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


# Login existing user
@main.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if not user or not check_password_hash(user.password, form.password.data):
            flash("Invalid email or password. Please try again.")
            return redirect(url_for('main.login'))

        login_user(user)
        return redirect(url_for("main.get_all_posts"))

    return render_template("login.html", current_user=current_user, form=form)


# Logout user
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Static Pages
@main.route('/about')
def about():
    return render_template("about.html", current_user=current_user)


@main.route('/contact')
def contact():
    return render_template("contact.html", current_user=current_user)
