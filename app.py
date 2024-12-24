from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulate a simple user database
users = {}

# Dictionary to store short URLs and their corresponding long URLs
url_mapping = {}

# Dictionary to store user-specific URLs
user_urls = {}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email  # Add email attribute

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return users.get(int(user_id))

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
    user_id = current_user.id
    urls = user_urls.get(user_id, [])  # Get the user's shortened URLs
    return render_template('dashboard.html', urls=urls)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if request.method == 'POST':
        email = request.form['email']  # Use email instead of username
        password = request.form['password']
        remember = 'remember' in request.form  # Check if 'remember me' is selected

        user = next((u for u in users.values() if u.email == email), None)  # Check email instead of username
        
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

        if any(u.username == username for u in users.values()):
            flash('Username already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        new_id = len(users) + 1
        user = User(id=new_id, username=username, password=generate_password_hash(password), email=email)  # Pass email to User
        users[new_id] = user

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
            # Generate a unique short ID (for demonstration purposes)
            short_id = str(uuid.uuid4()).replace('-', '')[:5]
            url_mapping[short_id] = long_url  # Store the mapping

            # Store user-specific data
            if current_user.is_authenticated:
                user_id = current_user.id
                if user_id not in user_urls:
                    user_urls[user_id] = []
                user_urls[user_id].append({
                    'short_id': short_id,
                    'long_url': long_url,
                    'clicks': 0  # Initialize click count
                })

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
    if short_id in url_mapping:
        original_long_url = url_mapping[short_id]

        # Increment click count for the user's URL
        for user_id, urls in user_urls.items():
            for url in urls:
                if url['short_id'] == short_id:
                    url['clicks'] += 1
                    break

        flash(f'Redirecting to {original_long_url}', 'info')
        return redirect(original_long_url)
    else:
        flash('Invalid short ID.', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)