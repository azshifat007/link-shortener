from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulate a simple user database
users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return users.get(int(user_id))

@app.route('/')
def home():
    """Home page."""
    return render_template('index.html')

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
    return render_template('pricing.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page, accessible only when logged in."""
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users.values() if u.username == username), None)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register route."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if any(u.username == username for u in users.values()):
            flash('Username already exists. Please log in.', 'warning')
            return redirect(url_for('login'))

        new_id = len(users) + 1
        user = User(id=new_id, username=username, password=generate_password_hash(password))
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

    if request.method == 'POST':
        long_url = request.form.get('long_url')
        if long_url:
            short_id = str(hash(long_url))[:6]  # Simple hash for demo purposes
            short_url = f"short.ly/{short_id}"

    return render_template('shorten.html', short_url=short_url, long_url=long_url)

@app.route('/short.ly/<short_id>')
def redirect_to_long_url(short_id):
    """Redirect from short URL to long URL."""
    flash('This is a placeholder. Implement URL mapping logic here.', 'info')
    return redirect(url_for('home'))  # Replace with the actual redirection logic

if __name__ == '__main__':
    app.run(debug=True)
