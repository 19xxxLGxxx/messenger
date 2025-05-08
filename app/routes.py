from flask import Blueprint, render_template, request, redirect, url_for, session
from . import db
from .models import User, Message

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["username"] = username

        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        return redirect(url_for("main.chat_list"))
    return render_template("login.html")

@bp.route("/chats")
def chat_list():
    if "username" not in session:
        return redirect(url_for("main.login"))

    current_user = User.query.filter_by(username=session["username"]).first()

    # Alle eindeutigen Kontakte aus gesendeten und empfangenen Nachrichten
    sent_ids = db.session.query(Message.recipient_id).filter_by(sender_id=current_user.id).distinct()
    received_ids = db.session.query(Message.sender_id).filter_by(recipient_id=current_user.id).distinct()

    contact_ids = {user_id for (user_id,) in sent_ids.union(received_ids).all()}
    contacts = User.query.filter(User.id.in_(contact_ids)).all()

    return render_template("chat_list.html", contacts=contacts, username=current_user.username)

@bp.route("/chat/<recipient_username>", methods=["GET", "POST"])
def chat(recipient_username):
    if "username" not in session:
        return redirect(url_for("main.login"))

    sender = User.query.filter_by(username=session["username"]).first()
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
def start_chat():
    recipient_username = request.form["recipient"]
    if not recipient_username:
        return "Name is required!", 400

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        recipient = User(username=recipient_username)
        db.session.add(recipient)
        db.session.commit()

    return redirect(url_for("main.chat", recipient_username=recipient_username))