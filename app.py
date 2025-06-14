from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'lekoysecret'
UPLOAD_FOLDER = 'static/uploads'
VIDEO_DB = 'videos.json'

# Tạo thư mục upload nếu chưa có
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tài khoản admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lekoy93'

def load_videos():
    if not os.path.exists(VIDEO_DB):
        return []
    with open(VIDEO_DB, 'r', encoding='utf-8') as f:
        try:
            videos = json.load(f)
        except:
            return []
        for v in videos:
            if isinstance(v.get("upload_date"), str):
                try:
                    v["upload_date"] = datetime.strptime(v["upload_date"], "%Y-%m-%d %H:%M:%S")
                except:
                    v["upload_date"] = datetime.now()
            elif "upload_date" not in v:
                v["upload_date"] = datetime.now()
        return videos

def save_videos(videos):
    with open(VIDEO_DB, 'w', encoding='utf-8') as f:
        for v in videos:
            if isinstance(v.get("upload_date"), datetime):
                v["upload_date"] = v["upload_date"].strftime("%Y-%m-%d %H:%M:%S")
        json.dump(videos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    videos = load_videos()
    approved = [v for v in videos if v.get('approved')]
    return render_template('index.html', videos=approved)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('upload'))
        else:
            return 'Sai thông tin'
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

        videos = load_videos()
        videos.append({
            "title": title,
            "url": url,
            "category": category,
            "upload_date": datetime.now(),
            "uploader": "admin",
            "approved": True
        })
        save_videos(videos)
        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/category/<cat>')
def category(cat):
    videos = load_videos()
    filtered = [v for v in videos if v.get("approved") and v.get("category") == cat]
    return render_template('category.html', videos=filtered, category=cat)

if __name__ == '__main__':
    app.run(debug=True)
