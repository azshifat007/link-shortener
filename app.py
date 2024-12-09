from flask import Flask, request, redirect, render_template, url_for, flash
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL
            )
        ''')
    print("Database initialized!")

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        if not original_url:
            flash("URL is required!", "error")
            return redirect(url_for('index'))

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()

            # Check if URL is already shortened
            cursor.execute("SELECT short_code FROM urls WHERE original_url = ?", (original_url,))
            existing = cursor.fetchone()
            if existing:
                short_code = existing[0]
            else:
                short_code = generate_short_code()
                cursor.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                               (original_url, short_code))
                conn.commit()

        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
        result = cursor.fetchone()
        if result:
            return redirect(result[0])
        else:
            return "URL not found!", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
