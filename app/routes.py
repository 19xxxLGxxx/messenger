from flask import Blueprint, render_template, request, redirect, url_for, session
from . import db
from .models import Message

bp = Blueprint("main", __name__)

@bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session['username'] = request.form['username']
        return redirect(url_for('main.chat_list'))
    return render_template("login.html")

@bp.route("/chats")
def chat_list():
    if 'username' not in session:
        return redirect(url_for('main.login'))

    username = session['username']
    sent = db.session.query(Message.recipient).filter_by(sender=username)
    received = db.session.query(Message.sender).filter_by(recipient=username)

    contacts = set()
    for s in sent:
        contacts.add(s.recipient)
    for r in received:
        contacts.add(r.sender)

    return render_template("chat_list.html", contacts=contacts, username=username)

@bp.route("/chat/<recipient>", methods=["GET", "POST"])
def chat(recipient):
    if 'username' not in session:
        return redirect(url_for('main.login'))

    sender = session['username']

    if request.method == 'POST':
        content = request.form['content']
        new_message = Message(sender=sender, recipient=recipient, content=content)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('main.chat', recipient=recipient))

    messages = Message.query.filter(
        ((Message.sender == sender) & (Message.recipient == recipient)) |
        ((Message.sender == recipient) & (Message.recipient == sender))
    ).order_by(Message.created_at).all()

    return render_template("chat.html", messages=messages, sender=sender, recipient=recipient)

@bp.route("/start_chat", methods=["POST"])
def start_chat():
    recipient = request.form['recipient']
    if not recipient:
        return "Name is required!", 400
    return redirect(url_for('main.chat', recipient=recipient))
