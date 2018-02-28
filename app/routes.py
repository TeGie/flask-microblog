from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Tomek'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Frosty day in Cieszyce'
        },
        {
            'author': {'username': 'Paul'},
            'body': 'Everything is so cool'
        }
    ]
    return render_template(
        'index.html', title='Home', user=user, posts=posts
    )
