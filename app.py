from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'lekoy-secret-key'  # Dùng cho session

# Tài khoản mẫu
users = {
    'admin': {'password': 'lekoy93', 'role': 'admin'},
    'guest': {'password': '123', 'role': 'guest'}
}

DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load video từ file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Lưu video
def save_data(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

# Convert URL thành iframe embed
def convert_url_to_embed(url):
    if "youtube.com/watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "facebook.com" in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif "vimeo.com/" in url:
        video_id = url.split("vimeo.com/")[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    else:
        return url

@app.route('/')
def index():
    videos = load_data()
    approved_videos = [v for v in videos if v.get('approved')]
    return render_template('index.html', videos=approved_videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('index'))
        error = "Sai tài khoản hoặc mật khẩu"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return "<h3>Bạn không có quyền đăng video. Chỉ admin mới được đăng!</h3>"

    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        embed_url = convert_url_to_embed(url)
        videos = load_data()
        videos.append({
            'title': title,
            'url': embed_url,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'approved': True
        })
        save_data(videos)
        return redirect(url_for('index'))

    return render_template('upload.html')
