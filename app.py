import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'lekoy_secret'

UPLOAD_FOLDER = 'videos'
DB_FILE = 'database.db'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            category TEXT,
            upload_date TEXT,
            approved INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    videos = conn.execute("SELECT * FROM videos WHERE approved = 1 ORDER BY id DESC").fetchall()
    conn.close()

    # Chuyển đổi upload_date thành datetime nếu có thể
    for video in videos:
        if isinstance(video['upload_date'], str):
            try:
                video['upload_date'] = datetime.strptime(video['upload_date'], '%Y-%m-%d')
            except Exception:
                video['upload_date'] = None
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'lekoy93':
            session['logged_in'] = True
            return redirect(url_for('upload'))
        else:
            error = 'Sai tài khoản hoặc mật khẩu!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        now = datetime.now().strftime('%Y-%m-%d')

        conn.execute("INSERT INTO videos (title, url, category, upload_date, approved) VALUES (?, ?, ?, ?, 1)",
                     (title, convert_to_embed(url), category, now))
        conn.commit()
        return redirect(url_for('upload'))

    videos = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('upload.html', videos=videos)

@app.route('/category/<cat>')
def category(cat):
    conn = get_db_connection()
    videos = conn.execute("SELECT * FROM videos WHERE category = ? AND approved = 1 ORDER BY id DESC", (cat,)).fetchall()
    conn.close()

    # Chuyển đổi upload_date nếu cần
    for video in videos:
        if isinstance(video['upload_date'], str):
            try:
                video['upload_date'] = datetime.strptime(video['upload_date'], '%Y-%m-%d')
            except Exception:
                video['upload_date'] = None
    return render_template("category.html", videos=videos, category=cat)

def convert_to_embed(url):
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    if 'youtube.com' in hostname or 'youtu.be' in hostname:
        if 'youtu.be' in hostname:
            video_id = parsed.path[1:]
        else:
            query = parsed.query
            video_id = query.split('v=')[-1].split('&')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif 'facebook.com' in hostname:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif 'vimeo.com' in hostname:
        return url.replace("vimeo.com", "player.vimeo.com/video")
    else:
        return url  # Giữ nguyên nếu không nhận dạng được

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
