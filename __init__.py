import sql
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def exctractFirstNumber(input):
    result = str("")
    for ch in input:
        if ch.isnumeric():
            result += ch
    return int(result)

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        if not login:
            flash('Login is required!')
        elif not password:
            flash('Password is required!')
        else:
            conn = sql.create_db_connection("localhost", "flask_server", "otus", "social_net")
            id = sql.execute_query(conn, 'SELECT id FROM creds WHERE login=\'{}\' and pwd=\'{}\''.format(login, password))
            print("<<<<<<<<<<<< id is {}".format(id))
            conn.close()
            return redirect(url_for('profile', user_id = id[0][0]))    
    
    return render_template('index.html')


@app.route('/<int:user_id>', methods=('GET', 'POST'))
def profile(user_id):
    if request.method == 'POST':
        fname = request.form['fname']
        sname = request.form['sname']        
        return redirect(url_for('sresults', user_id = user_id, fname = fname, sname = sname))
                
    conn = sql.create_db_connection("localhost", "flask_server", "otus", "social_net")
    profile = sql.execute_query(conn, 'SELECT fname, sname, age, gender, hob, city FROM profile WHERE crid={}'.format(user_id))
    frids = sql.execute_query(conn, 'SELECT frid FROM friends WHERE userid={}'.format(user_id))
    print(frids)

    friends = []
    for frid in frids:
        fsname = sql.execute_query(conn, 'SELECT fname, sname FROM profile WHERE crid={}'.format(frid[0]))
        print(type(fsname))
        print(fsname)        
        friends.append(fsname)
    print(profile)
    print(friends)
    conn.close()

    return render_template('profile.html', profile = profile, friends = friends)

@app.route('/registration', methods=('GET', 'POST'))
def registration():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        fname = request.form['fname']
        sname = request.form['sname']
        gender = request.form['gender']
        age = request.form['age']
        hobbies = request.form['hobbies']
        city = request.form['city']       

        if not login:
            flash('Login is required!')
        elif not password:
            flash('Password is required!')
        else:
            conn = sql.create_db_connection("localhost", "flask_server", "otus", "social_net")
            sql.execute_query(conn, 'INSERT INTO creds (login, pwd) VALUES (\'{}\', \'{}\')'.format(login, password))
            crid = sql.execute_query(conn, 'SELECT id FROM creds WHERE login=\'{}\' and pwd=\'{}\''.format(login, password))
            print("<<<<<<<<<<<< crid is {}".format(crid))
            sql.execute_query(conn, 
            'INSERT INTO profile (crid, fname, sname, age, gender, hob, city) VALUES ({},\'{}\',\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(
                crid[0][0], fname, sname, age, gender, hobbies, city))
            conn.close()

            return redirect(url_for('profile', user_id = crid[0][0]))
    return render_template('registration.html')

@app.route('/<int:user_id>&<string:fname>&<string:sname>/sresults', methods=('GET', 'POST'))
def sresults(user_id, fname, sname):

    conn = sql.create_db_connection("localhost", "flask_server", "otus", "social_net")
    if request.method == 'POST':
        friendId = request.form['friendId']
        friendId = exctractFirstNumber(friendId)        
        sql.execute_query(conn, 'INSERT INTO friends (userid, frid) VALUES ({}, {})'.format(user_id, friendId))

    profile_ids = sql.execute_query(conn, 'SELECT crid FROM profile WHERE fname=\'{}\' and sname=\'{}\''.format(fname, sname))
    friend_ids = sql.execute_query(conn, 'SELECT frid FROM friends WHERE userid={}'.format(user_id))
    conn.close()
    return render_template('sresults.html', user_id = user_id, 
    profile_ids = profile_ids, friend_ids = friend_ids, fname = fname, sname = sname)