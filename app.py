from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Lưu video tạm thời trong bộ nhớ
videos = []

@app.route('/')
def index():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    filtered = [
        v for v in videos
        if (search.lower() in v['title'].lower()) and
           (category == '' or category == v['category'])
    ]
    categories = sorted(set(v['category'] for v in videos))
    return render_template('index.html', videos=filtered, categories=categories)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        url = request.form['url']
        videos.append({'title': title, 'description': description, 'category': category, 'url': url})
        return redirect(url_for('index'))
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
