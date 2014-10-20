#-*- coding: utf-8 -*-

import sqlite3
import os
from flask import *

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database/eh.db'),
    DEBUG=True,
    # 生成秘钥
    SECRET_KEY=os.urandom(24),
    USERNAME='admin',
    PASSWORD='default'
))

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def welcome():
    if session.get('logged_in'):
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        return render_template('dashboard.html', user = user)
    else:
        return redirect(url_for('login'))

# 简化sqlite3的查询方式。
def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_l = None
    if request.method == 'POST':
        user = query_db('select * from user where username = ?', [request.form['username']], one=True)
        if user is None:
            error_l = u"用户名不存在。"
        else:
            if request.form['password'] != user['password']:
                error_l = u"密码不正确。"
            else:
                session['username'] = request.form['username']
                session['logged_in'] = True;
                return redirect(url_for('welcome'));
        # 注册新用户。
        # g.db.execute('insert into user (username, password) values (?, ?)', [request.form['username'], request.form['password']])
        # g.db.commit()
    return render_template("welcome.html", error_l = error_l)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_r = None
    if request.method == 'POST':
        user = query_db('select * from user where username = ?', [request.form['username']], one=True)
        if user is not None:
            error_r = u"用户名重复。"
        else:
            # 注册新用户。
            g.db.execute('insert into user (username, password) values (?, ?)', [request.form['username'], request.form['password']])
            g.db.commit()
            return redirect(url_for('welcome'));
    return render_template("welcome.html", error_r = error_r)

# 退出登录。
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# 投条。
@app.route('/post', methods=['GET', 'POST'])
def postOrder():
    if session.get('logged_in'):
        if request.method == 'POST':
            if request.form.get('is_anonymity'):
                g.db.execute('insert into item (username, content, is_anonymity) values (?, ?, ?)', [session['username'], request.form['content'], request.form['is_anonymity']])
            else:
                g.db.execute('insert into item (username, content) values (?, ?)', [session['username'], request.form['content']])
            g.db.commit()
            return redirect(url_for('welcome'))
        return render_template('postOrder.html')
    else:
        return redirect(url_for('welcome'))

# 接单表。
@app.route('/get')
def getOrder():
    return render_template('getOrder.html')

# 活动页面。
@app.route('/event')
def eventActivity():
    return render_template('eventActivity.html')

# 个人设置页面。
@app.route('/setting')
def personalSetting():
    return render_template('personalSetting.html')

@app.route('/test/<username>')
def show_user_profile(username):
    return '你好 %s' % username

@app.route('/test/<int:post_id>')
def show_post(post_id):
    return '你投送了 %d' % post_id

@app.route('/location')
def showLocation():
    return render_template('showLocation.html')

@app.route('/home')
def homePage():
    return render_template('homePage.html')

@app.route('/hello')
def showHello():
    return render_template('showHello.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    app.run(debug=True)