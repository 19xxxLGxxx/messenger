from app import create_app, db
from os import path, makedirs

app = create_app()
db_path = path.join(path.dirname(__file__), "instance", "db.db")

if __name__ == "__main__":
    makedirs(path.dirname(db_path), exist_ok=True)
    with app.app_context():
        db.create_all()
        print("Datenbank erzeugt:", path.exists(db_path))
    app.run(debug=True)
