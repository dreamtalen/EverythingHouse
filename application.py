#-*- coding: utf-8 -*-

import sqlite3
import os
from flask import *
import time as time

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
        return redirect(url_for('homePage'))
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

# 注册。
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
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        user['notification'] = user['notification'].split('###')
        if request.method == 'POST':
            if request.form.get('is_anonymity'):
                g.db.execute('insert into item (username, content, is_anonymity, position, time) values (?, ?, ?, ?, ?)', [session['username'], request.form['content'].strip(' '), request.form['is_anonymity'], request.form['position'], request.form['time']])
            else:
                g.db.execute('insert into item (username, content, position, time) values (?, ?, ?, ?)', [session['username'], request.form['content'].strip(' '), request.form['position'], request.form['time']])
            g.db.commit()
            return render_template('postOrder.html', user = user)
        return render_template('postOrder.html', user = user)
    else:
        return redirect(url_for('welcome'))

# 接单表。
@app.route('/get')
def getOrder():
    if session.get('logged_in'):
        error = None
        if request.args.get('error'):
            error = request.args.get('error')
        success = None
        if request.args.get('success'):
            success = request.args.get('success')
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        user['notification'] = user['notification'].split('###')
        orders = query_db('select * from item')
        orders.reverse()
        local_time_array = time.localtime()
        for order in orders:
            get_time_array = time.strptime(order['time'], u"%Y年%m月%d日%H时%M分")
            if get_time_array.tm_year - local_time_array.tm_year == 0:
                if get_time_array.tm_mon - local_time_array.tm_mon == 0:
                    if get_time_array.tm_mday - local_time_array.tm_mday == 0:
                        if get_time_array.tm_hour - local_time_array.tm_hour == 0:
                            order['time'] = str(local_time_array.tm_min-get_time_array.tm_min)+u"分钟前"
                        else:
                            order['time'] = str(local_time_array.tm_hour-get_time_array.tm_hour)+u"小时前"
                    else:
                        order['time'] = str(local_time_array.tm_mday-get_time_array.tm_mday)+u"天前"
                else:
                    order['time'] = str(local_time_array.tm_mon-get_time_array.tm_mon)+u"月前"
            else:
                order['time'] = str(local_time_array.tm_year-get_time_array.tm_year)+u"年前"
        return render_template('getOrder.html', orders = orders, user = user, error = error, success = success)
    else:
        return redirect(url_for('welcome'))

# 交易
@app.route('/deal/<int:post_id>')
def dealOrder(post_id):
    error = None
    success = None
    if session.get('logged_in'):
        post_state = query_db('select state from item where id = ?', [post_id], one=True)
        if post_state['state'] == 1:
            error = u"这个单子已经处于交易中！"
            return redirect(url_for('getOrder', error = error))
        elif post_state['state'] == 0:
            username = query_db('select username from item where id = ?', [post_id], one=True)
            if username['username'] == session['username']:
                error = u"你不能接受自己的投条！"
                return redirect(url_for('getOrder', error = error))
            g.db.execute('update item set state = 1, dealername = ? where id = ?', [session['username'], post_id])
            g.db.commit()
            post_letter = session['username']+u"向你ID为"+str(post_id)+u"的订单发起交易。###"
            g.db.execute('update user set notification = ? where username = ?', [post_letter, username['username']])
            g.db.commit()
        return redirect(url_for('getOrder', success = u"操作成功~"))
    else:
        return redirect(url_for('welcome'))

# 活动页面。
@app.route('/event')
def eventActivity():
    if session.get('logged_in'):
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        user['notification'] = user['notification'].split('###')
        return render_template('eventActivity.html', user = user)
    else:
        return render_template('eventActivity.html')

# 个人设置页面。
@app.route('/setting')
def personalSetting():
    if session.get('logged_in'):
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        user['notification'] = user['notification'].split('###')
        return render_template(
            'personalSetting.html', user = user)
    else:
        return render_template('personalSetting.html')

# 主页页面。
@app.route('/home')
def homePage():
    if session.get('logged_in'):
        user = query_db('select * from user where username = ?', [session['username']], one=True)
        user['notification'] = user['notification'].split('###')
        post_orders = query_db('select * from item where username = ?', [session['username']])
        get_orders = query_db('select * from item where dealername = ?', [session['username']])
        deal_orders = query_db('select * from item where username = ? and state = 1', [session['username']])
        post_orders.reverse();
        get_orders.reverse();
        deal_orders.reverse();
        local_time_array = time.localtime()
        for order in post_orders:
            post_time_array = time.strptime(order['time'], u"%Y年%m月%d日%H时%M分")
            if post_time_array.tm_year - local_time_array.tm_year == 0:
                if post_time_array.tm_mon - local_time_array.tm_mon == 0:
                    if post_time_array.tm_mday - local_time_array.tm_mday == 0:
                        if post_time_array.tm_hour - local_time_array.tm_hour == 0:
                            order['time'] = str(local_time_array.tm_min-post_time_array.tm_min)+u"分钟前"
                        else:
                            order['time'] = str(local_time_array.tm_hour-post_time_array.tm_hour)+u"小时前"
                    else:
                        order['time'] = str(local_time_array.tm_mday-post_time_array.tm_mday)+u"天前"
                else:
                    order['time'] = str(local_time_array.tm_mon-post_time_array.tm_mon)+u"月前"
            else:
                post_orders[0]['time'] = str(local_time_array.tm_year-post_time_array.tm_year)+u"年前"
        for order in get_orders:
            get_time_array = time.strptime(order['time'], u"%Y年%m月%d日%H时%M分")
            if get_time_array.tm_year - local_time_array.tm_year == 0:
                if get_time_array.tm_mon - local_time_array.tm_mon == 0:
                    if get_time_array.tm_mday - local_time_array.tm_mday == 0:
                        if get_time_array.tm_hour - local_time_array.tm_hour == 0:
                            order['time'] = str(local_time_array.tm_min-get_time_array.tm_min)+u"分钟前"
                        else:
                            order['time'] = str(local_time_array.tm_hour-get_time_array.tm_hour)+u"小时前"
                    else:
                        order['time'] = str(local_time_array.tm_mday-get_time_array.tm_mday)+u"天前"
                else:
                    order['time'] = str(local_time_array.tm_mon-get_time_array.tm_mon)+u"月前"
            else:
                order['time'] = str(local_time_array.tm_year-get_time_array.tm_year)+u"年前"
        for order in deal_orders:
            get_time_array = time.strptime(order['time'], u"%Y年%m月%d日%H时%M分")
            if get_time_array.tm_year - local_time_array.tm_year == 0:
                if get_time_array.tm_mon - local_time_array.tm_mon == 0:
                    if get_time_array.tm_mday - local_time_array.tm_mday == 0:
                        if get_time_array.tm_hour - local_time_array.tm_hour == 0:
                            order['time'] = str(local_time_array.tm_min-get_time_array.tm_min)+u"分钟前"
                        else:
                            order['time'] = str(local_time_array.tm_hour-get_time_array.tm_hour)+u"小时前"
                    else:
                        order['time'] = str(local_time_array.tm_mday-get_time_array.tm_mday)+u"天前"
                else:
                    order['time'] = str(local_time_array.tm_mon-get_time_array.tm_mon)+u"月前"
            else:
                order['time'] = str(local_time_array.tm_year-get_time_array.tm_year)+u"年前"
        return render_template('homePage.html', post_orders = post_orders, get_orders = get_orders, deal_orders = deal_orders, user = user)
    else:
        return redirect(url_for('welcome'))

@app.route('/test/<username>')
def show_user_profile(username):
    return '你好 %s' % username

@app.route('/test/<int:post_id>')
def show_post(post_id):
    return '你投送了 %d' % post_id

@app.route('/location')
def showLocation():
    return render_template('showLocation.html')

@app.route('/hello')
def showHello():
    return render_template('showHello.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == "__main__":
    app.run(debug=True)