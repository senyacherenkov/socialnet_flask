from pickle import FALSE
from engine.sql_db import create_db_connection, execute_query, execute_file, execute_list_query
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

sql_HOST = "localhost"
sql_USER = "flask_server"
sql_PWD = "otus"
sql_DBNAME = "social_net"

#def readConfig(filepath):

def exctractFirstNumber(input):
    result = str("")
    for ch in input:
        if ch.isnumeric():
            result += ch
    return int(result)

def exctractCreds(request):
    data = {}
    badResult = {"profile": "none"}
    auth = request.authorization
    headers = request.headers
    if auth and auth.get('username'):
        if not auth.get('password'):
            flash('No password provided via basic auth.')
            return badResult
        data['username'] = auth['username']
        data['token'] = auth['password']
    elif 'X-Auth-Token' in headers and 'X-Auth-From' in headers:
        if not headers.get('X-Auth-Token'):
            flash('No X-Auth-Token provided via auth headers.')
            return badResult
        data['username'] = headers['X-Auth-From']
        data['token'] = headers['X-Auth-Token']
    else:
        flash('Login is required!')
        return badResult
    return data

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        
        creds = exctractCreds(request)
        if len(creds) > 1:
            conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)
            id = execute_query(conn, 'SELECT id FROM creds WHERE login=\'{}\' and pwd=\'{}\''.format(creds['username'], str(hash(creds['token']))))
            print("<<<<<<<<<<<< id is {}".format(id))
            conn.close()
            if len(id):
                return redirect(url_for('profile', id = id[0][0]))
        else:
            return creds

    return {"profile": "none"}


@app.route('/profile', methods=('GET', 'POST'))
def profile():
    user_id = request.args.get('id')
    print(">>>>>>>>>>>>> user_id: {}".format(user_id))

    if request.method == 'POST':
        fname = request.form['fname']
        sname = request.form['sname']        
        return redirect(url_for('sresults', user_id = user_id, fname = fname, sname = sname))
                
    conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)    
    profile = execute_query(conn, 'SELECT fname, sname, age, gender, hob, city FROM profile WHERE crid={}'.format(user_id))
    frids = execute_query(conn, 'SELECT frid FROM friends WHERE userid={}'.format(user_id))
    print(frids)

    if len(profile):
        profileDict = {}
        profileDict["id"] = user_id
        profileDict["First name"] = profile[0][0]
        profileDict["Second name"] = profile[0][1]  
        profileDict["Age"] = profile[0][2] 
        profileDict["Gender"] = profile[0][3] 
        profileDict["Hobbies"] = profile[0][4] 
        profileDict["City"] = profile[0][5] 
        friends = []
        for frid in frids:
            fsname = execute_query(conn, 'SELECT fname, sname FROM profile WHERE crid={}'.format(frid[0]))
            print(type(fsname))
            print(fsname)        
            friends.append(fsname)
        print(profile)
        print(friends)
        conn.close()

        profileDict["Friends"] = friends 

        return profileDict
    return {"profile": "none"}

@app.route('/registration', methods=('GET', 'POST'))
def registration():
    print("in registration handler")
    
    if request.method == 'POST':
        creds = exctractCreds(request)
        print("<<<<<<<<<<<< login: {}, pwd: {}".format(creds['username'], creds['token']))
        
        fname = request.args.get('fname')
        sname = request.args.get('sname')
        gender = request.args.get('gender')
        age = request.args.get('age')
        hobbies = request.args.get('hobbies')
        city = request.args.get('city')

        print("<<<<<<<<<<<< fname: {}, sname: {}, gender: {}, age: {}, hobbies: {}, city: {}".format(fname, sname, gender, age, hobbies, city))
        
        
        if len(creds) > 1:
            conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)           
            execute_query(conn, 'INSERT INTO creds (login, pwd) VALUES (\'{}\', \'{}\')'.format(creds['username'], str(hash(creds['token']))))
            crid = execute_query(conn, 'SELECT id FROM creds WHERE login=\'{}\' and pwd=\'{}\''.format(creds['username'], str(hash(creds['token']))))
            print("<<<<<<<<<<<< crid is {}".format(crid))
            print(fname)
            execute_query(conn, 
            'INSERT INTO profile (crid, fname, sname, age, gender, hob, city) VALUES ({},\'{}\',\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(
                crid[0][0], fname, sname, age, gender, hobbies, city))
            conn.close()

            return redirect(url_for('profile', id = crid[0][0]))
    return {"result": "none"}

@app.route('/addFriend', methods=('GET', 'POST'))
def sresults():
    user_id = request.args.get('profileId')
    fname = request.args.get('fname')
    sname = request.args.get('sname')
        
    if request.method == 'POST':
        conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)
        profile_ids = execute_query(conn, 'SELECT crid FROM profile WHERE fname=\'{}\' and sname=\'{}\''.format(fname, sname))
        friend_ids = execute_query(conn, 'SELECT frid FROM friends WHERE userid={}'.format(user_id))

        if len(profile_ids):
            for prid in profile_ids:
                execute_query(conn, 'INSERT INTO friends (userid, frid) VALUES ({}, {})'.format(user_id, prid[-1]))
                execute_query(conn, 'INSERT INTO friends (userid, frid) VALUES ({}, {})'.format(prid[-1], user_id))

            conn.close()
            
            data = {}

            for prid in profile_ids:
                friendData = {}
                friendData["fname"] = fname
                friendData["sname"] = sname
                friendData["status"] = "now your friend"
                if prid in friend_ids:
                    friendData["status"] = "already your friend"
                data["result"] = friendData
            return data
        else:
            return {"result": "cannot find this person"}
    return {"result": "none"}
    