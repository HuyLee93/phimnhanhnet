from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
def convert_video_url(url_input):
    if "youtube.com/watch?v=" in url_input:
        video_id = url_input.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in url_input:
        video_id = url_input.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "facebook.com" in url_input:
        return f"https://www.facebook.com/plugins/video.php?href={url_input}&show_text=0&width=560"
    elif "vimeo.com/" in url_input:
        video_id = url_input.split("vimeo.com/")[-1].split("?")[0]
        return f"https://player.vimeo.com/video/{video_id}"
    else:
        return url_input

app = Flask(__name__)
app.secret_key = 'lekoy93_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Khởi tạo DB nếu chưa có
def init_db():
    with get_db_connection() as conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())
    print("✅ DB Initialized")

@app.route('/')
def index():
    conn = get_db_connection()
    videos = conn.execute("SELECT * FROM videos WHERE approved = 1 ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'lekoy93':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Sai tài khoản hoặc mật khẩu'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        url = convert_video_url(request.form['url'])  # dùng hàm mới
        category = request.form['category']
        conn = get_db_connection()
        conn.execute("INSERT INTO videos (title, url, category, approved, uploader) VALUES (?, ?, ?, 0, ?)",
                     (title, url, category, 'guest'))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        video_id = request.form['video_id']
        action = request.form['action']
        if action == 'approve':
            conn.execute("UPDATE videos SET approved = 1 WHERE id = ?", (video_id,))
        elif action == 'delete':
            conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()

    videos = conn.execute("SELECT * FROM videos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin.html', videos=videos)
@app.route('/category/<cat>')
def category(cat):
    conn = get_db_connection()
    videos = conn.execute("SELECT * FROM videos WHERE approved = 1 AND category = ? ORDER BY id DESC", (cat,)).fetchall()
    conn.close()
    return render_template('category.html', videos=videos, category=cat)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
