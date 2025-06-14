from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json
import os
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'lekoy-secret-key'

DATA_FILE = 'data/videos.json'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lekoy93'

def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_videos(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

def convert_to_embed(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        if 'watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif 'facebook.com' in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif 'vimeo.com' in url:
        video_id = url.split('/')[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    else:
        # fallback: dùng iframe trực tiếp
        return url

@app.route('/')
def index():
    videos = load_videos()
    approved = [v for v in videos if v.get('approved')]
    return render_template('index.html', videos=approved)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('upload'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        embed_url = convert_to_embed(url)
        now = datetime.now().strftime('%Y-%m-%d')

        new_video = {
            'title': title,
            'url': embed_url,
            'upload_date': now,
            'category': category,
            'approved': True  # vì admin đăng nên tự động duyệt
        }

        videos = load_videos()
        videos.append(new_video)
        save_videos(videos)

        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/pending')
def pending():
    if not session.get('admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    unapproved = [v for v in videos if not v.get('approved')]
    return render_template('pending.html', videos=unapproved)

@app.route('/approve/<int:video_id>')
def approve(video_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    videos = load_videos()
    if 0 <= video_id < len(videos):
        videos[video_id]['approved'] = True
        save_videos(videos)
    return redirect(url_for('pending'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
