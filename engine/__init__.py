from pickle import FALSE
from sql_db import *
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
import names_dataset
import random
import geonamescache
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

sql_HOST = "mysql"
sql_USER = "flask_server"
sql_PWD = "otus"
sql_DBNAME = "social_net"

RECORDS_NUMBER = 1000000
BATCH_RECORD_SIZE = 50
CURRENT_YEAR = 2022
LOWER_AGE_BORDER = 10
UPPER_AGE_BORDER = 99

HOBBIES = ["learning", "teaching", "football", "walking", "jogging", "diving", "gaming", "art", "cinema", "food", "travel", "cars", "bikes", "devices", "sports"]
GENDER = ["male", "female"]
CITIES = ["Moscow", "St.Petersburg", "Tegeran", "Beijin", "Kair", "Stambul", "Minsk", "Erevan", "Magadan", "Chili", "Kabul", "Rostov", "Tomsk", "Samara", "Kazan"]

class Profile:
    def __init__(self, fname = "sara", sname = "conor", age = 33, gender = "female", hobbies = "future saving", city = "Pasadena", login = "sc", pwd="nightmare"):
        self.fname = fname
        self.sname = sname
        self.age = age
        self.gender = gender
        self.hobbies = hobbies
        self.city = city
        self.login = login
        self.pwd = pwd

    def write2DB(self):
        conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)      
        execute_query(conn, 'INSERT INTO creds (login, pwd) VALUES (\'{}\', \'{}\')'.format(self.login, str(hash(self.pwd))))
        crid = execute_query(conn, 'SELECT id FROM creds WHERE login=\'{}\' and pwd=\'{}\''.format(self.login, str(hash(self.pwd))))
        execute_query(conn, 
        'INSERT INTO profile (crid, fname, sname, age, gender, hob, city) VALUES ({},\'{}\',\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(
            crid[0][0], self.fname, self.sname, self.age, self.gender, self.hobbies, self.city))
        conn.close()

def getNamesDict(filename):
    mn = []
    for line in open(filename):
        mn.append(line[:-2])
    return mn

def generateProfilesInDb():
    query = 'INSERT INTO profile (crid, fname, sname, age, gender, hob, city) VALUES '

    fn = getNamesDict('fnames.txt')
    sn = getNamesDict('snames.txt')

    conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)
    for i in range(int(RECORDS_NUMBER/BATCH_RECORD_SIZE)):
        for j in range(BATCH_RECORD_SIZE):
            fname = random.choice(fn)
            sname = random.choice(sn)
            age = random.randint(LOWER_AGE_BORDER, UPPER_AGE_BORDER)
            gender = random.choice(GENDER)
            hobbies = random.choice(HOBBIES)
            city = random.choice(CITIES)
            query += '({},\'{}\',\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(uuid.uuid4().int>>64, fname, sname, age, gender, hobbies, city)
            if j != BATCH_RECORD_SIZE - 1:
                query += ', '
    
        execute_query(conn, query)
        query = 'INSERT INTO profile (crid, fname, sname, age, gender, hob, city) VALUES '

    return query

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

@app.route('/generate', methods=('GET', 'POST'))
def generate():
    if request.method == 'POST':
        generateProfilesInDb()        
        return {"generate": "done"} 
    return {"generate": "error"}


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
        if len(creds) > 1:
            userProfile = Profile(request.args.get('fname'), 
                                request.args.get('sname'), 
                                request.args.get('gender'), 
                                request.args.get('age'), 
                                request.args.get('hobbies'), 
                                request.args.get('city'),
                                creds['username'],
                                creds['token'])
       
            userProfile.write2DB()

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

        user_id = int(user_id)
        if len(profile_ids):
            for prid in profile_ids:
                id = int(prid[-1])
                if prid[-1] != user_id:
                    execute_query(conn, 'INSERT INTO friends (userid, frid) VALUES ({}, {})'.format(user_id, prid[-1]))
                    execute_query(conn, 'INSERT INTO friends (userid, frid) VALUES ({}, {})'.format(prid[-1], user_id))
                else:
                    return {"result": "you cannot add yourself"}

            conn.close()
            
            data = {}
            data["result"] = []
            for prid in profile_ids:
                friendData = {}
                friendData["fname"] = fname
                friendData["sname"] = sname
                friendData["status"] = "now your friend"
                if prid in friend_ids:
                    friendData["status"] = "already your friend"
                data["result"].append(friendData)
            return data
        else:
            return {"result": "cannot find this person"}
    return {"result": "none"}

@app.route('/prefixSearch', methods=('GET', 'POST'))
def prefixSearch():
    fname = request.args.get('fname')
    sname = request.args.get('sname')
        
    if request.method == 'POST':
        conn = create_db_connection(sql_HOST, sql_USER, sql_PWD, sql_DBNAME)
        profiles = execute_query(conn, 'SELECT crid, fname, sname, age, gender, hob, city FROM profile WHERE fname LIKE \'{}%\' and sname LIKE \'{}%\' ORDER BY crid'.format(fname, sname))

        if len(profiles):
            
            data = {}
            data["result"] = []
            for profile in profiles:
                friendData = ""
                friendData += str(profile[0])
                friendData += str(", ")
                friendData += str(profile[1])
                friendData += str(", ")
                friendData += str(profile[2])
                friendData += str(", ")
                friendData += str(profile[3])
                friendData += str(", ")
                friendData += str(profile[4])
                friendData += str(", ")
                friendData += str(profile[5])
                friendData += str(", ")
                friendData += str(profile[6])
                
                data["result"].append(friendData)
            return data
        else:
            return {"result": "cannot find this person"}
    return {"result": "none"}
    