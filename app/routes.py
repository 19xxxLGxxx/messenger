from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message as MailMessage
from . import db, mail
from .models import User, Message

bp = Blueprint("main", __name__)
s = URLSafeTimedSerializer("abcd")

@bp.route("/")
def index():
    return render_template("start.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            print("Funktioniert")
            flash("E-Mail existiert bereits.")
            return redirect(url_for("main.register"))

        user = User(email=email, username=email.split("@")[0])
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = s.dumps(email, salt="email-confirm")
        confirm_url = url_for("main.confirm_email", token=token, _external=True)
        html = render_template("email/confirm.html", confirm_url=confirm_url)

        msg = MailMessage("Bitte bestätige deine Registrierung", recipients=[email], html=html)
        print(f"Sende Mail an {email} mit Link: {confirm_url}")
        try:
            mail.send(msg)
            print("Mail erfolgreich versendet.")
        except Exception as e:
            print("Mail-Versand fehlgeschlagen:", e)


        flash("Bestätigungs-E-Mail gesendet!")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@bp.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)
    except:
        flash("Link ungültig oder abgelaufen.")
        return redirect(url_for("main.login"))

    user = User.query.filter_by(email=email).first_or_404()
    if not user.is_verified:
        user.is_verified = True
        db.session.commit()
        flash("E-Mail bestätigt! Du kannst dich jetzt einloggen.")
    else:
        flash("E-Mail war bereits bestätigt.")
    return redirect(url_for("main.login"))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_verified:
                flash("Bitte bestätige zuerst deine E-Mail.")
                return redirect(url_for("main.login"))
            login_user(user)
            session["username"] = user.username
            return redirect(url_for("main.chat_list"))

        flash("Login fehlgeschlagen.")
    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("main.login"))

@bp.route("/chats")
@login_required
def chat_list():
    current_user_obj = current_user
    sent_ids = db.session.query(Message.recipient_id).filter_by(sender_id=current_user_obj.id).distinct()
    received_ids = db.session.query(Message.sender_id).filter_by(recipient_id=current_user_obj.id).distinct()

    contact_ids = {user_id for (user_id,) in sent_ids.union(received_ids).all()}
    contacts = User.query.filter(User.id.in_(contact_ids)).all()

    return render_template("chat_list.html", contacts=contacts, username=current_user_obj.username)

@bp.route("/chat/<recipient_username>", methods=["GET", "POST"])
@login_required
def chat(recipient_username):
    sender = current_user
    recipient = User.query.filter_by(username=recipient_username).first()

    if not recipient:
        return "Empfänger nicht gefunden", 404

    if request.method == "POST":
        content = request.form["content"]
        new_message = Message(sender_id=sender.id, recipient_id=recipient.id, content=content)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("main.chat", recipient_username=recipient_username))

    messages = Message.query.filter(
        ((Message.sender_id == sender.id) & (Message.recipient_id == recipient.id)) |
        ((Message.sender_id == recipient.id) & (Message.recipient_id == sender.id))
    ).order_by(Message.created_at).all()

    return render_template("chat.html", messages=messages, sender=sender.username, recipient=recipient.username)

@bp.route("/start_chat", methods=["POST"])
@login_required
def start_chat():
    recipient_username = request.form["recipient"]
    if not recipient_username:
        return "Name is required!", 400

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        recipient = User(username=recipient_username, email=f"{recipient_username}@example.com", password_hash="placeholder")
        db.session.add(recipient)
        db.session.commit()

    return redirect(url_for("main.chat", recipient_username=recipient_username))

@bp.route("/chat_data/<recipient_username>")
@login_required
def chat_data(recipient_username):
    sender = current_user
    recipient = User.query.filter_by(username=recipient_username).first()

    messages = Message.query.filter(
        ((Message.sender_id == sender.id) & (Message.recipient_id == recipient.id)) |
        ((Message.sender_id == recipient.id) & (Message.recipient_id == sender.id))
    ).order_by(Message.created_at).all()

    return render_template("chat_messages.html", messages=messages, sender=sender.username)
