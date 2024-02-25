# Import standard libraries
import os, random, rsa, string, smtplib
from datetime import datetime

# Import third-party libraries
from dotenv import load_dotenv
from functools import update_wrapper, wraps
from flask import Flask, render_template, request, redirect, url_for, abort, make_response, current_app, jsonify, session, flash
from flask_login import LoginManager, current_user, login_required, logout_user, login_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from werkzeug.security import generate_password_hash, check_password_hash

# Import local modules
from forms import LoginForm, RegistrationForm, PasswordForm

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    passwords = db.relationship('Password', backref='user', lazy=True)

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        # This should return True if the user's account is active, or False otherwise.
        # For now, we'll just always return True.
        return True
    
    @property
    def is_authenticated(self):
        # This should return True if the user is authenticated, or False otherwise.
        # For now, we'll just always return True.
        return True
    
class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(120), nullable=False)
    password = db.Column(EncryptedType(db.String, app.config['SECRET_KEY'], AesEngine, 'pkcs5'), nullable=False)
    rsa_encrypted_password = db.Column(db.LargeBinary, nullable=False)  # Add this line
    password_type = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
# RSA key generation
def get_rsa_keys():
    if not os.path.exists('public.pem') or not os.path.exists('private.pem'):
        # Generate a new key pair
        (public_key, private_key) = rsa.newkeys(2048)  # Increase key size to 2048

        # Save the keys to files
        with open('public.pem', 'wb') as f:
            f.write(public_key.save_pkcs1())
        with open('private.pem', 'wb') as f:
            f.write(private_key.save_pkcs1())
    else:
        # Load the keys from files
        with open('public.pem', 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open('private.pem', 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())

    return public_key, private_key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Delete cache after logging out
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

# Define routes
@app.route('/')
def home():
    return render_template('index.html', title='Home')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Incorrect credentials.'
            session['2fa_completed'] = False
        else:
            login_user(user)
            # Store the user's ID in the session
            session['user_id'] = user.id
            # Generate 2FA code and store it in the session
            session['2fa_code'] = random.randint(100000, 999999)
            print("2FA code:", session['2fa_code'])
            # Redirect the user to the 2FA verification page
            return redirect(url_for('verify_2fa'))
    return render_template('login.html', title='Sign In', form=form, error=error)

def login_and_2fa_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not session.get('2fa_completed', False):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Verify 2FA
@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if request.method == 'POST':
        user_code = request.form.get('2fa_code')
        if int(user_code) == session['2fa_code']:
            session['2fa_completed'] = True
            # User is fully authenticated
            user = User.query.get(session['user_id'])
            login_user(user)  # Log the user in again
            return redirect(url_for('view_passwords'))
        else:
            # Invalid 2FA code
            flash('Invalid 2FA code. Please try again.')
    return render_template('verify_2fa.html')

def send_email(to, subject, body):
    from email.mime.text import MIMEText
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your-email@example.com'
    msg['To'] = to

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

# Logout
@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            error = 'A user with this email already exists. Please choose a different email.'
        else:
            user = User(email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
    return render_template('register.html', title='Register', form=form, error=error)

# Add password
@app.route('/add_password', methods=['GET', 'POST'])
@login_and_2fa_required
@nocache
def add_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if form.password_type.data == 'random':
            password = generate_password(form.length.data, form.include_uppercase.data, form.include_lowercase.data, form.include_numbers.data, form.include_special.data)
        elif form.password_type.data == 'passphrase':
            password = generate_passphrase(form.length.data, form.capitalize.data, form.add_numbers.data, form.separator.data)
        else:
            password = form.password.data

        # Get the RSA keys
        public_key, private_key = get_rsa_keys()

        # Encrypt the password with RSA
        rsa_encrypted_password = rsa.encrypt(password.encode(), public_key)

        password = Password(website=form.website.data, password=password, rsa_encrypted_password=rsa_encrypted_password, password_type=form.password_type.data, user_id=current_user.id)
        db.session.add(password)
        db.session.commit()
        return redirect(url_for('view_passwords'))
    return render_template('add_password.html', title='Add Password', form=form)

# View passwords
@app.route('/view_passwords')
# @login_required
@login_and_2fa_required
@nocache
def view_passwords():
    password_type = request.args.get('password_type', 'all')
    query = request.args.get('query', '')
    if password_type == 'random':
        passwords = Password.query.filter(Password.user_id == current_user.id, Password.password_type == 'random', Password.website.contains(query)).all()
    elif password_type == 'passphrase':
        passwords = Password.query.filter(Password.user_id == current_user.id, Password.password_type == 'passphrase', Password.website.contains(query)).all()
    else:
        passwords = Password.query.filter(Password.user_id == current_user.id, Password.website.contains(query)).all()
    return render_template('view_passwords.html', title='View Passwords', passwords=passwords, password_type=password_type)

# Edit password
@app.route('/edit_password/<int:id>', methods=['GET', 'POST'])
@login_and_2fa_required
@nocache
def edit_password(id):
    password = Password.query.get_or_404(id)
    if password.user_id != current_user.id:
        abort(403)
    form = PasswordForm(obj=password)
    if form.validate_on_submit():
        password.password_type = form.password_type.data
        password.password = form.password.data  # Ensure the password is updated
        db.session.commit()
        return redirect(url_for('view_passwords'))
    return render_template('edit_password.html', title='Edit Password', form=form, password=password)

# Delete password
@app.route('/delete_password/<int:id>', methods=['POST'])
def delete_password(id):
    password = Password.query.get_or_404(id)
    if password.user_id != current_user.id:
        abort(403)
    db.session.delete(password)
    db.session.commit()
    return redirect(url_for('view_passwords'))

# Define utility functions
# Generate password
@app.route('/generate_password', methods=['POST'])
def generate_password_route():
    length = request.form.get('length', type=int)
    use_random_password = request.form.get('use_random_password', type=bool)
    use_passphrase = request.form.get('use_passphrase', type=bool)
    include_uppercase = request.form.get('include_uppercase', type=bool)
    include_lowercase = request.form.get('include_lowercase', type=bool)
    include_numbers = request.form.get('include_numbers', type=bool)
    include_special = request.form.get('include_special', type=bool)
    capitalize = request.form.get('capitalize', type=bool)
    add_numbers = request.form.get('add_numbers', type=bool)
    separator = request.form.get('separator')
    if use_random_password:
        password = generate_password(length, include_uppercase, include_lowercase, include_numbers, include_special)
    elif use_passphrase:
        password = generate_passphrase(length, capitalize, add_numbers, separator)
    else:
        password = ''
    return jsonify(password=password)

# Generate random characters
def generate_password(length=10, include_uppercase=True, include_lowercase=True, include_numbers=True, include_special=True):
    characters = ""
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_lowercase:
        characters += string.ascii_lowercase
    if include_numbers:
        characters += string.digits
    if include_special:
        characters += string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# Generate passphrases
import requests
import random

def get_words():
    response = requests.get("https://api.datamuse.com/words?ml=fruit")
    words = response.json()
    return [word['word'] for word in words]

def generate_passphrase(num_words=4, capitalize=False, add_numbers=False, separator=' '):
    words = get_words()
    passphrase = []
    for _ in range(num_words):
        word = random.choice(words)
        if capitalize:
            word = word.capitalize()
        if add_numbers:
            word += str(random.randint(0, 9))
        passphrase.append(word)
    return separator.join(passphrase)
