import re, json, os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = 'lekoysecret'

# “Database” giả lập
DATA_FILE = 'videos.json'
users = {'admin': {'pw': 'lekoy93', 'role': 'admin'}}

def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_videos(videos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

videos = load_videos()

def convert_embed(url):
    if re.search(r'youtu\.?be', url):
        vid = re.findall(r'(?:v=|\.be/)([^&?/]+)', url)[0]
        return f"https://www.youtube.com/embed/{vid}"
    if 'vimeo.com' in url:
        vid = url.rsplit('/', 1)[-1]
        return f"https://player.vimeo.com/video/{vid}"
    if 'facebook.com' in url:
        return f"https://www.facebook.com/plugins/video.php?href={url}"
    return url

@app.route('/')
def index():
    q = request.args.get('q', '').lower()
    cat = request.args.get('category', '')
    filtered = [v for v in videos if v.get('approved', False)
                and (q in v['title'].lower())
                and (cat == '' or cat == v['category'])]
    return render_template('index.html', videos=filtered, user=session.get('user'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u, p = request.form['username'], request.form['password']
        if u in users and users[u]['pw'] == p:
            session['user'] = u
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')
    if request.method=='POST':
        url = convert_embed(request.form['url'])
        new_video = {
            'id': len(videos),
            'title': request.form['title'],
            'url': url,
            'category': request.form['category'],
            'user': session['user'],
            'approved': session['user']=='admin',
            'likes': 0,
            'dislikes': 0,
            'comments': []
        }
        videos.append(new_video)
        save_videos(videos)
        return redirect('/')
    return render_template('upload.html')

@app.route('/delete/<int:vid>')
def delete(vid):
    global videos
    if session.get('u
