# Dependencies / Requirements

Creating database

```bash
python3
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

```bash
pip install flask
pip install flask_sqlalchemy
pip install flask_login
pip install sqlalchemy-utils
pip install Werkzeug
pip install flask_wtf
pip install cryptography
pip install email_validator
pip install python-dotenv
pip install rsa
pip install requests
```

Then modify the database path in app.py file.
