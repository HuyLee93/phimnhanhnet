from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'lekoy_secret_key'
UPLOAD_FOLDER = 'static/videos'
DATA_FILE = 'data/videos.json'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# ================================
# Utility functions
# ================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_videos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_videos(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

# ================================
# Routes
# ================================

@app.route('/')
def index():
    videos = load_videos()
    approved_videos = [v for v in videos if v.get('approved', True)]
    return render_template('index.html', videos=approved_videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'lekoy93':
            session['admin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        url = request.form['url']
        category = request.form['category']
        new_video = {
            'id': str(uuid.uuid4()),
            'title': title,
            'url': url,
            'category': category,
            'approved': session.get('admin', False),
            'likes': 0,
            'dislikes': 0,
            'comments': [],
            'upload_t_
