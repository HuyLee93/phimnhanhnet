from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import json

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # xử lý đăng nhập ở đây
        pass
    return render_template('login.html')

DATA_FILE = 'data.json'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load video data từ file JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Lưu video data
def save_data(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)

# Chuyển URL thành embed iframe
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
        return url  # Trường hợp mặc định nếu không nhận diện được

@app.route('/')
def index():
    videos = load_data()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        embed_url = convert_url_to_embed(url)
        videos = load_data()
        videos.append({
            'title': title,
