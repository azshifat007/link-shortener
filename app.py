from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import uuid
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///link_shortener.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for Flask-Login
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('shortened_urls', lazy=True))

# Create database tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    """Home page."""
    return render_template('index.html', title='Home', is_home=True)

@app.route('/terms')
def terms():
    """Terms and Conditions page."""
    return render_template('terms_and_conditions.html')

@app.route('/privacy')
def privacy():
    """Privacy Policy page."""
    return render_template('privacy_policy.html')

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/pricing')
def pricing():
    """Pricing page."""
    return render_template('pricing.html', title='Pricing', is_home=False)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page, accessible only when logged in."""
    urls = ShortenedURL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if request.method == 'POST':
        email = request.form['email']  # Use email instead of username
        password = request.form['password']
        remember = 'remember' in request.form  # Check if 'remember me' is selected

        user = User.query.filter_by(email=email).first()  # Query the database for the user
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)  # Pass 'remember' to login_user
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Add email field

        # Check if the username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Create a new user
        new_user = User(username=username, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/shorten', methods=['GET', 'POST'])
def shorten_url():
    """URL Shortener."""
    short_url = None
    long_url = None
    qr_code_img = None

    if request.method == 'POST':
        long_url = request.form.get('long_url')
        if long_url:
            short_id = str(uuid.uuid4()).replace('-', '')[:5]

            # Save the shortened URL to the database
            if current_user.is_authenticated:
                new_url = ShortenedURL(short_id=short_id, long_url=long_url, user_id=current_user.id)
                db.session.add(new_url)
                db.session.commit()

            short_url = f"short.ly/{short_id}"

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(short_url)
            qr.make(fit=True)

            img = qr.make_image(fill='black', back_color='white')

            # Save QR code as a base64 encoded image
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code_img = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render_template('shorten.html', short_url=short_url, long_url=long_url, qr_code_img=qr_code_img)

@app.route('/short.ly/<short_id>')
def redirect_to_long_url(short_id):
    """Redirect from short URL to long URL."""
    url = ShortenedURL.query.filter_by(short_id=short_id).first()
    if url:
        url.clicks += 1
        db.session.commit()
        flash(f'Redirecting to {url.long_url}', 'info')
        return redirect(url.long_url)
    else:
        flash('Invalid short ID.', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)