import re
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'lekoysecret'

# “Database” giả lập
videos = []
users = {'admin': {'pw': 'lekoy93', 'role': 'admin'}}

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
    filtered = [v for v in videos if v['approved']
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
        videos.append({
            'id': len(videos),
            'title': request.form['title'],
            'url': url,
            'category': request.form['category'],
            'user': session['user'],
            'approved': session['user']=='admin',
            'likes':0,'dislikes':0,'comments':[]
        })
        return redirect('/')
    return render_template('upload.html')

@app.route('/delete/<int:vid>')
def delete(vid):
    if session.get('user')=='admin':
        videos[:] = [v for v in videos if v['id'] != vid]
    return redirect('/')

@app.route('/like/<int:vid>')
def like(vid):
    videos[vid]['likes'] += 1
    return redirect('/')

@app.route('/dislike/<int:vid>')
def dislike(vid):
    videos[vid]['dislikes'] += 1
    return redirect('/')

@app.route('/comment/<int:vid>', methods=['POST'])
def comment(vid):
    name=session.get('user','Khách')
    videos[vid]['comments'].append({'user':name,'txt':request.form['comment']})
    return redirect('/')

@app.route('/watch/<int:vid>')
def watch(vid):
    return render_template('video.html', video=videos[vid])

@app.route('/ping')
def ping():
    return 'pong'
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
