from flask import Flask, render_template, request, redirect, session, url_for
from urllib.parse import urlparse, parse_qs
import re

app = Flask(__name__)
app.secret_key = 'lekoysecret'

videos = []
users = {'admin': {'password': 'lekoy93', 'role': 'admin'}, 'guest': {'password': '123', 'role': 'guest'}}

def convert_to_embed(url):
    if "youtube.com" in url or "youtu.be" in url:
        video_id = ''
        if "youtu.be" in url:
            video_id = url.split("/")[-1]
        elif "youtube.com" in url:
            video_id = parse_qs(urlparse(url).query).get("v", [""])[0]
        return f"https://www.youtube.com/embed/{video_id}"
    elif "facebook.com" in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    elif "vimeo.com" in url:
        video_id = url.split("/")[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    elif "dailymotion.com" in url:
        video_id = re.search(r'/video/([^_]+)', url)
        return f"https://www.dailymotion.com/embed/video/{video_id.group(1)}" if video_id else url
    return url

@app.route('/')
def index():
    q = request.args.get('q', '')
    cat = request.args.get('category', '')
    results = [v for v in videos if (q.lower() in v['title'].lower()) and (cat == '' or v['category'] == cat) and v['approved']]
    return render_template('index.html', videos=results, username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        if u in users and users[u]['password'] == p:
            session['username'] = u
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        url = convert_to_embed(request.form['url'])
        cat = request.form['category']
        approved = users[session['username']]['role'] == 'admin'
        videos.append({'title': title, 'url': url, 'category': cat, 'approved': approved, 'comments': [], 'likes': 0, 'dislikes': 0, 'user': session['username']})
        return redirect('/')
    return render_template('upload.html')

@app.route('/delete/<int:idx>')
def delete(idx):
    if 'username' in session and users[session['username']]['role'] == 'admin':
        videos.pop(idx)
    return redirect('/')

@app.route('/like/<int:idx>')
def like(idx):
    videos[idx]['likes'] += 1
    return redirect('/')

@app.route('/dislike/<int:idx>')
def dislike(idx):
    videos[idx]['dislikes'] += 1
    return redirect('/')

@app.route('/comment/<int:idx>', methods=['POST'])
def comment(idx):
    cmt = request.form['comment']
    videos[idx]['comments'].append({'user': session.get('username', 'ẩn danh'), 'text': cmt})
    return redirect('/')

@app.route('/category/<name>')
def category(name):
    return render_template('category.html', videos=[v for v in videos if v['category'] == name and v['approved']], category=name)
