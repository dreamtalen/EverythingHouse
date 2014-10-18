#-*- coding: utf-8 -*-

import sqlite3
import os
from flask import *

app = Flask(__name__)

# 生成秘钥
app.secret_key = os.urandom(24)
print app.secret_key

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.route('/')
def index():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # 检查数据库，先略过。
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'));
    return render_template('welcome.html')

@app.route('/hello')
def hello():
    return 'Hello World!!!'

@app.route('/1/<username>')
def show_user_profile(username):
    return '你好 %s' % username

@app.route('/1/<int:post_id>')
def show_post(post_id):
    return '你投送了 %d' % post_id

@app.route('/1/about/')
def show_about_page():
    return 'This is the ABOUT page.'

@app.route('/2/')
def show_location():
    return render_template('index.html')

@app.route('/3/')
def show_helloHTML():
    return render_template('hello.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    app.run(debug=True)