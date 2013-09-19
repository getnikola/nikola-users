import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    data = (
        ('site name', 'http://google.com', 'author', 'desc', 'sourcelink'),
        ('another', 'http://example.com', 'authorette', 'ription', None),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
    )
    return render_template('index.html', data=data)

@app.route('/add/', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        # Temporary.
        return render_template('add.html')
    else:
        return render_template('add.html')

@app.route('/edit/')
def edit():
    return render_template('edit-remove.html', action='edit')

@app.route('/remove/')
def remove():
    return render_template('edit-remove.html', action='remove')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
