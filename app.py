from flask import Flask, request, redirect, render_template, url_for, flash, session
import sqlite3
import string
import random
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                click_count INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        print("Database initialized!")

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in first!", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url:
            flash("URL is required!", "error")
            return redirect(url_for('index'))

        short_code = generate_short_code()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)', (original_url, short_code))
                conn.commit()
                flash(f"Shortened URL created: {request.host_url}{short_code}", "success")
            except sqlite3.IntegrityError:
                flash("Error creating short URL.", "error")

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT original_url, click_count FROM urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()
        if result:
            original_url, click_count = result
            cursor.execute('UPDATE urls SET click_count = ? WHERE short_code = ?', (click_count + 1, short_code))
            conn.commit()
            return redirect(original_url)
        else:
            flash("Short URL not found!", "error")
            return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['user_id'] = user[0]
                flash("Logged in successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "error")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                flash("Account created successfully!", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already taken!", "error")
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT original_url, short_code, click_count FROM urls')
        urls = cursor.fetchall()
    return render_template('dashboard.html', urls=urls)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
