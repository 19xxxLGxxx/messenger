from unittest.mock import patch
from flask import url_for


def test_register_user(client, app):
    print("Datenbank-URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    with patch("app.routes.mail.send") as mock_send:
        response = client.post("/register", data={
            "email": "testuser@example.com",
            "password": "testpassword"
        }, follow_redirects=True)

        assert response.status_code == 200

        assert mock_send.called

        with app.app_context():
            from app.models import User
            user = User.query.filter_by(email="testuser@example.com").first()
            assert user is not None
            assert user.is_verified is False
