from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)

    sent_messages = db.relationship(
        "Message",
        foreign_keys='Message.sender_id',
        lazy=True
    )

    received_messages = db.relationship(
        "Message",
        foreign_keys='Message.recipient_id',
        lazy=True
    )

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])

    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, nullable=True)
