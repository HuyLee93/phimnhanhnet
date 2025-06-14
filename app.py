from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import json, os, re

app = Flask(__name__)
app.secret_key = 'lekoy-secret'

VIDEO_FILE = 'videos.json'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'lekoy93'

# Load video list from file
def load_videos():
    if not os.path.exists(VIDEO_FILE):
        return []
    with open(VIDEO_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save video list to file
def save_videos(videos):
    with open(VIDEO_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2, default=str)

# Convert URL to embed iframe-compatible URL
def convert_to_embed(url):
    if "youtube.com/watch?v=" in url:
        video_id = url.split("watch?v=")[-1].split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "facebook.com" in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif "vimeo.com/" in url:
        match = re.search(r"vimeo.com/(\\d+)", url)
        if match:
            return f"https://player.vimeo.com/video/{match.group(1)}"
    elif "tiktok.com" in url:
        return f"https://www.tiktok.com/embed/{url.split('/')[-1]}"
    return url

videos = load_videos()

@app.route('/')
def index():
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
        video = {
            'title': title,
            'url': embed_url,
            'category': category,
            'approved': True,
            'upload_date': datetime.now().strftime('%Y-%m-%d')
        }
        videos.append(video)
        save_videos(videos)
        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/category/<cat>')
def category(cat):
    filtered = [v for v in videos if v.get('approved') and v.get('category') == cat]
    return render_template('category.html', videos=filtered, category=cat)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
