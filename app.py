import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import uuid
import qrcode
from io import BytesIO
import base64
import logging

# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')  # Use a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///link_shortener.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Shortened URL model
class ShortenedURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(10), unique=True, nullable=False)
    long_url = db.Column(db.String(500), nullable=False)
    clicks = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Allow NULL for non-signed-up users
    user = db.relationship('User', backref=db.backref('shortened_urls', lazy=True))
    qr_code_img = db.Column(db.Text)

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    user_logged_in = 'user' in session
    return render_template('index.html', title='Home', is_home=True, show_navbar=False, user_logged_in=user_logged_in)

@app.route('/terms')
def terms():
    return render_template('terms_and_conditions.html', show_navbar=True)

@app.route('/privacy')
def privacy():
    return render_template('privacy_policy.html', show_navbar=True)

@app.route('/about')
def about():
    return render_template('about.html', is_home=False, show_navbar=True)

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', title='Pricing', is_home=False, show_navbar=True)

@app.route('/dashboard')
@login_required
def dashboard():
    urls = ShortenedURL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls, show_navbar=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            session['user_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', show_navbar=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', show_navbar=True)

@app.route('/logout')
@login_required
def logout():
    session.pop('user_logged_in', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():
    short_url = None
    long_url = None
    qr_code_img = None

    if request.method == 'POST':
        long_url = request.form.get('long_url')
        if long_url:
            # Initialize the session counter for non-signed-up users
            if not current_user.is_authenticated:
                if 'link_count' not in session:
                    session['link_count'] = 0  # Initialize the counter if it doesn't exist

                # Check if the user has reached the limit
                if session['link_count'] >= 10:
                    flash('You have reached the limit of 10 shortened links. Please sign up to create more.', 'warning')
                    return redirect(url_for('shorten_url'))

            short_id = str(uuid.uuid4()).replace('-', '')[:5]

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"short.ly/{short_id}")
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code_img = base64.b64encode(buffered.getvalue()).decode('utf-8')

            # Save the URL for both authenticated and non-authenticated users
            if current_user.is_authenticated:
                new_url = ShortenedURL(short_id=short_id, long_url=long_url, user_id=current_user.id, qr_code_img=qr_code_img)
            else:
                new_url = ShortenedURL(short_id=short_id, long_url=long_url, user_id=None, qr_code_img=qr_code_img)
                session['link_count'] += 1  # Increment the counter for non-signed-up users

            db.session.add(new_url)
            db.session.commit()

            short_url = f"short.ly/{short_id}"

    return render_template('shorten.html', short_url=short_url, long_url=long_url, qr_code_img=qr_code_img, show_navbar=True)

@app.route('/short.ly/<short_id>')
def redirect_to_long_url(short_id):
    url = ShortenedURL.query.filter_by(short_id=short_id).first()
    if url:
        url.clicks += 1
        db.session.commit()
        flash(f'Redirecting to {url.long_url}', 'info')
        return redirect(url.long_url)
    else:
        flash('Invalid short ID.', 'error')
        return redirect(url_for('home'), show_navbar=True)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f'404 Error: {e}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f'500 Error: {e}')
    return render_template('500.html'), 500

# Run the app
if __name__ == '__main__':
    # Ensure debug mode is off in production
    app.run(host="0.0.0.0", port=5000, debug=False)