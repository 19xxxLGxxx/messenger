from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "instance", "db.db")

app = Flask(__name__)
app.secret_key = 'abcd'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(200), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=True)

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('chat_list'))
    return render_template('login.html')

@app.route("/chats")
def chat_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    sent = db.session.query(Message.recipient).filter_by(sender=username)
    received = db.session.query(Message.sender).filter_by(recipient=username)

    contacts = set()
    for s in sent:
        contacts.add(s.recipient)
    for r in received:
        contacts.add(r.sender)

    return render_template('chat_list.html', contacts=contacts, username=username)

@app.route("/chat/<recipient>", methods=['GET', 'POST'])
def chat(recipient):
    if 'username' not in session:
        return redirect(url_for('login'))

    sender = session['username']

    if request.method == 'POST':
        content = request.form['content']
        new_message = Message(sender=sender, recipient=recipient, content=content)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat', recipient=recipient))

    messages = Message.query.filter(
        ((Message.sender == sender) & (Message.recipient == recipient)) |
        ((Message.sender == recipient) & (Message.recipient == sender))
    ).order_by(Message.created_at).all()

    return render_template('chat.html', messages=messages, sender=sender, recipient=recipient)

@app.route('/start_chat', methods=['POST'])
def start_chat():
    recipient = request.form['recipient']
    if not recipient:
        return "Name is required!", 400
    return redirect(url_for('chat', recipient=recipient))

if __name__ == "__main__":
    os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)

    with app.app_context():
        db.create_all()
        print("Datenbank erzeugt:", os.path.exists(db_path))

    app.run(debug=True)