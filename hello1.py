import os
import time
import datetime
import pytz
import smtplib




from flask import Flask, url_for, request, render_template, redirect, flash, make_response, session, jsonify
import logging
import pymysql
from flask_restful import reqparse, abort, Api, Resource
from logging.handlers import RotatingFileHandler
import uuid
def get_auth_token():
    return uuid.uuid4().hex
from itsdangerous import (TimedJSONWebSignatureSerializer
    as Serializer, BadSignature, SignatureExpired)  

    
app = Flask(__name__)

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('token')
parser.add_argument('sentto', action='append')
parser.add_argument('message')

@app.route('/api/token')
def send_auth_token():
    cursor,conn = cursorcreate()
    username = request.values['username']
    password= request.values['password']
    cursor.execute('SELECT * FROM user WHERE username="%s" AND password="%s"' % (username, password))
    data = cursor.fetchone()
    if data:
        
        return jsonify({'usernamefillerfiller':username, 'token':generate_auth_token(data[0]).decode('ascii')})
    else:
        return jsonify({'errorfillerfillerfiller':'username and password not found'})
        
@app.route('/api/getmessage')
def getmessagesapi():
    cursor, conn = cursorcreate()
    args = parser.parse_args()
    username = verify_auth_token(request.values["token"])
    if username != None:
        json = {'usernamefillerfiller':username}
        cursor.execute('SELECT * FROM messagesid WHERE to_user = "%s"' % (username))
        data = cursor.fetchall()
        for datapiece in data:
            cursor.execute('SELECT * FROM messages WHERE message_id = "%s"' % (datapiece[2]))
            info = cursor.fetchone()
            print(datapiece[0])
            if datapiece[0] in json:
                json[datapiece[0]][str(info[2])] = str(info[1])
            else:
                json[datapiece[0]] = {}
                json[datapiece[0]][str(info[2])] = str(info[1])
        print(json)
        return jsonify(json)
    else:
        return jsonify({"errorfillerfillerfiller":"token not found"})
    
        
def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        cursor, conn = cursorcreate()
        cursor.execute('SELECT * FROM user WHERE user_id="%s"' % (data['id']))
        data=cursor.fetchone()
        return data[1]
@app.route('/api/sendmessage')
def apisendmessage():
    cursor, conn = cursorcreate()
    args = parser.parse_args()
    token = request.values["token"]
    sentto = request.values["sentto"]
    message = request.values["message"]
    if verify_auth_token(token) != None:
        username = verify_auth_token(token)
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        pst_now = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))
        string = pst_now.isoformat()
        string = string.replace('T', ' ')
        string = string.split('.')[0]
        print(message + ' ' + string + ' ' + str(sentto))
        cursor.execute('INSERT INTO messages(message, datetime) VALUES ("%s", "%s")' % (message, string))
        conn.commit()
        
        cursor.execute('SELECT * FROM messages WHERE datetime="%s" AND message="%s"' % (string, message))
        data = cursor.fetchone()
        messageid = data[0]
        for user in sentto:
            print('hi')
            cursor.execute('INSERT INTO messagesid(sending_user, to_user, message_id) VALUES ("%s", "%s", "%s")' % (username, user, messageid))
            conn.commit()
            
        return jsonify({"info": "%s send message %s to %s" % (username, message, sentto)})
    else:
        return "Token not found."
    
        
@app.route('/api/resource')
def get_resource():
    token = request.values["token"]
    if verify_auth_token(token) != None:
        return jsonify({ 'data': '%s!' % verify_auth_token(token) })
    else:
        return jsonify({"errorfillerfillerfiller": "token not found"})
        

def generate_auth_token(id, expiration = 600):
    s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
    return s.dumps({ 'id': id })
    

@app.route('/invite', methods=['GET','POST'])
def invite():
    if request.method == 'POST':
        content = "You have been invited to a website!"

        mail=  smtplib.SMTP('smtp.gmail.com', 587)

        mail.ehlo()

        mail.starttls()

        mail.login('elephantism150@gmail.com', 'fadman777')
        
        print(request.form['sendto'])

        mail.sendmail('elephantism150@gmail.com',request.form['sendto'],content)

        mail.close
        
        flash('Succesfully invited!')
        return redirect('/')
    return render_template('invite.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor, conn = cursorcreate()
    error = None
    if request.method == 'POST':
        if validLogin(request.form['username'], request.form['password']) == True:
            cursor.execute("SELECT * FROM admins WHERE username='%s'" % (request.form['username']))
            data = cursor.fetchall()
            print('hue')
            if data:
                USERS = {}
                print('ha')
                USERS = {'username':request.form.get('username'), 'password':request.form.get('password'), 'token':get_auth_token()}
                print('ha')
                session['username']=request.form.get('username')
                session['admin'] = True
                print('kek')
                return render_template('json.html', json=USERS) 
            else:
                USERS = {}
                USERS = {'username':request.form.get('username'), 'password':request.form.get('password'), 'token':get_auth_token()}
                session['username']=request.form.get('username')
                return render_template('json.html', json=USERS) 
        else:
            error = 'Incorrect username and password.'
            app.logger.warning("Incorrect username and password for user (%s)", request.form.get('username'))
    return render_template('login.html', error=error)


@app.route('/deleteaccount', methods=["GET", "POST"])
def delete_account():
    cursor, conn = cursorcreate()
    if 'admin' in session:
        if request.method == "POST":
            info = request.form.getlist('toUser')
            for users in info:
                cursor.execute('DELETE FROM user WHERE username="%s"' % (users))
                conn.commit()
                cursor.execute('DELETE FROM messagesid WHERE to_user="%s"' % (users))
                conn.commit()
                cursor.execute('DELETE FROM messagesid WHERE sending_user="%s"'%(users))
                conn.commit()
            flash("Succesfully deleted accounts!")
            return redirect('/')
        return render_template('deleteaccount.html', multiselect=convert_multi_select())
    else:
        return redirect("/")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
    
@app.route('/deleteMail')
def deleteMail():
    cursor, conn = cursorcreate()
    cursor.execute('DELETE FROM messagesid WHERE message_id = "%s" and to_user = "%s"'%(request.values['messageid'], session['username']))
    conn.commit()
    flash('Message deleted!')
    return redirect('/')
    
    
@app.route('/', methods=["GET","POST"])
def welcome():
    cursor, conn = cursorcreate()
    
    if 'username' in session:
        seconds = 30
        if request.method == "POST":
            return redirect(url_for('welcome'))
        cursor.execute('SELECT * FROM messagesid WHERE to_user="%s"' % session['username'])
        data = cursor.fetchall()
        tmparr = []
        for i in range(0, len(data)):
            tmparr.append(data[len(data) - i - 1])
        data = tmparr
        print(data)
        table = '<div id="table-wrapper"><div id="table-scroll"><table border="1", scrolling="yes", bordercolor="green">'
        table += '<tr><th>Time</th><th>Sender</th><th>Message</th><th>Reply To All</th><th>Reply</th><th>Delete</th>'
        for i in range(0, len(data)):
            table += '<tr>'
            cursor.execute('SELECT * FROM messages WHERE message_id = "%s"'%(data[i][2]))
            message = cursor.fetchone()
            print('message:' + str(message))
            table += '<td>%s</td><td>%s</td><td>%s</td><td><a href="/reply?messageid=%s">Reply to All</a></td><td><a href="/replyOne?messageid=%s">Reply to Sender</a></td><td><a href="/deleteMail?messageid=%s">Delete Mail</a></td>' % (message[2], data[i][0],message[1], data[i][2], data[i][2], data[i][2])
            table += '</tr>'
        table += "</table></div></div>"
        return render_template('welcome.html', username=session['username'], table=table)
        
        
    else:
        return redirect(url_for('login'))
        

        
        
def html_table(info):
  string = '<div id="table-wrapper"><div id="table-scroll"><table border="1", scrolling="yes", bordercolor="green">'
  string += '<tr><th>Sender</th><th>Message</th><th>Reply</th>'
  for sublist in info:
    string += '<tr>'
    string += '<td>%s</td><td>%s</td><td><a href="/reply?username=%s">Reply</a></td>' % (sublist[1], sublist[3], sublist[1])
    string += '</tr>'
  string += '</table>'
  string += '</div></div>'
  return string
    
def validLogin(username, password):
    cursor, conn = cursorcreate()
    invalid_character_array = ["{", "[", "}", "]", "-", "_", "=", "+", "~", "`", " ", "'", "\""]
    if any(x in username for x in invalid_character_array):
        return False
    elif any(x in password for x in invalid_character_array):
        return False
    elif password == '' or username =='':
        return False
    else:
        cursor.execute('SELECT * from user WHERE username="%s" AND password="%s"' % (username, password))
        data = cursor.fetchone()
        if data:
            return True
        else:
            return False
        
        
@app.route('/signin', methods = ["GET", "POST"])
def signin():
    invalid_character_array = ["{", "[", "}", "]", "-", "_", "=", "+", "~", "`", " "]
    error = None 
    cursor, conn = cursorcreate()
    if request.method == "POST":
        if any(x in request.form.get('username') for x in invalid_character_array):
            error = "Invalid character in username!"
        elif any(x in request.form.get('password') for x in invalid_character_array):
            error = "Invalid character in password!"
        else:
            if request.form.get('password') == request.form.get('confirm') and request.form.get('username') != '' and request.form.get('password') != '' and 64 >= len(request.form.get('username')) >= 6 and 64 >= len(request.form.get('password')) >= 6:
                cursor.execute('SELECT * FROM user WHERE username="%s"' % (request.form.get('username')))
                data = cursor.fetchone()
                if data:
                    error = "Username taken"
                else:
                    cursor.execute("INSERT INTO user(username, password) VALUES('%s', '%s');" % (request.form.get('username'), request.form.get('password')))
                    conn.commit()
                    USERS = {}
                    USERS = {'username': request.form.get('username'), 'password': request.form.get('password'), 'token':get_auth_token()}
                    session['username']=request.form.get('username')
                    return render_template('json.html', json=USERS)
            
            elif request.form.get('password') == '':
                error = "Not a valid password."
            elif request.form.get('username') == '':
                error = "Not a valid username."
            elif 64 < len(request.form.get('username')) or len(request.form.get('username')) < 6:
                error = "Username has to be between 6 and 64 characters!"
            elif 64 < len(request.form.get('password')) or len(request.form.get('password')) < 6:
                error = "Password has to be between 6 and 64 characters!" 
            elif request.form.get('password') != request.form.get('confirm'):
                error = "Passwords don't match."
    return render_template('signin.html', error=error)
    
    
    
@app.route('/sendmessage', methods=["GET", "POST"])
def sendmessage():
    cursor, conn = cursorcreate()
    error = None
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    pst_now = utc_now.astimezone(pytz.timezone("America/Los_Angeles"))

    string = pst_now.isoformat()
    string = string.replace('T', ' ')
    string = string.split('.')[0]
    datetimestr = datetime.datetime.now()
    datetimestr = str(datetimestr).split('.')[0]
    if 'replyAll' in session:
        multiselect = convert_multi_select_reply(session['replyAll'])
    elif 'replyOne' in session:
        multiselect = convert_multi_select_reply(session['replyOne'])
    else:
        multiselect = convert_multi_select()
    if 'username' in session:
        if request.method == "POST":
            if request.form.getlist('toUser'):
                info = request.form.getlist('toUser')
                inputstring = request.form.get('message').replace('\\', '\\\\')
                inputstring = inputstring.replace("'", "\\'")
                inputstring = inputstring.replace('"', '\\"')
                print(inputstring)
                cursor.execute('INSERT INTO messages(message, datetime) VALUES("%s", "%s")' % (inputstring, string))
                conn.commit()
                for i in range(0, len(info)):
                    databaseURL(request.form.get('message'), info[i], session['username'])
                MESSAGES = {}
                MESSAGES = {'time':string, 'sender':session['username'], 'sent to':info, 'message':inputstring}
                return render_template('json.html', json=MESSAGES)
            else:
                error = "Not sending to a user!"
    else:
        return redirect(url_for('login'))
        
    return render_template('postlink.html', error=error, multiselect=multiselect)
    
@app.route('/sentmail')
def sentmail():
    if 'username' in session:
        cursor, conn = cursorcreate()
        used=  []
        string = '<div id="table-wrapper"><div id="table-scroll"><table border="1", scrolling="yes", bordercolor="green">'
        string += '<tr><th>Date</th><th>Sent To</th><th>Message</th>'
        cursor= conn.cursor()
        cursor.execute('SELECT * FROM messagesid WHERE sending_user="%s"'%(session['username']))
        data = cursor.fetchall()
        sameMail = -1
        sameString = ''
        for info in data:
            if info[2] == sameMail:
                sameString += str(info[1])
                sameString += ', '
            elif sameMail == -1:
                sameMail = info[2]
                sameString += str(info[1])
                sameString += ', '
            else:
                cursor.execute('SELECT * FROM messages WHERE message_id="%s"'%(sameMail))
                finalinfo = cursor.fetchone()
                string += '<tr>' 
                string += '<td>%s</td><td>%s</td><td>%s</td>' % (finalinfo[2], sameString[:-2], finalinfo[1])
                string += '</tr>'
                sameMail = info[2]
                sameString = str(info[1])
                sameString += ', '
            
            if info==data[-1]:
                cursor.execute('SELECT * FROM messages WHERE message_id="%s"'%(sameMail))
                finalinfo = cursor.fetchone()
                string += '<tr>' 
                string += '<td>%s</td><td>%s</td><td>%s</td>' % (finalinfo[2], sameString[:-2], finalinfo[1])
                string += '</tr>'
        string +=  '</table>'
        string += '</div></div>'
        
        return render_template('sentmail.html', sentmail=string)
    else:
        return redirect('/login')
    
def databaseURL(message, user, sendingUser):
    cursor, conn = cursorcreate()
    error = None
    message = message.replace('\\', '\\\\')
    message = message.replace("'", "\\'")
    message = message.replace('"', '\\"')
    cursor.execute('SELECT message_id FROM messages WHERE message="%s"'%(message))
    number = cursor.fetchall()[-1]
    cursor.execute('INSERT INTO messagesid(sending_user, to_user, message_id) VALUES("%s", "%s", "%s")'%(sendingUser, user, number[0]))
    conn.commit()
    return error
    
    
        
        
def convert_multi_select():
    cursor, conn = cursorcreate()
    cursor.execute('SELECT username FROM user')
    data = cursor.fetchall()
    string = "<select multiple id='multiselect' name='toUser'>"
    
    for users in data:
        string += '<option value="%s">%s</option>' % (users[0], users[0])
    string += '</select>'
    return string
    
    
def convert_multi_select_reply(messageid):
    cursor, conn = cursorcreate()
    cursor.execute('SELECT username FROM user')
    data = cursor.fetchall()
    string = "<select multiple id='multiselect' name='toUser'>"
    if 'replyAll' in session:
        cursor.execute('SELECT * FROM messagesid WHERE message_id = "%s"' % (messageid))
        info = cursor.fetchall()
        correctArr = []
        correctArr.append(info[0][0])
        for i in range(0, len(info)):
            if info[i][1] != session['username']:
                correctArr.append(info[i][1])
    
        for users in data:
            if users[0] not in correctArr:
                string += '<option value="%s">%s</option>' % (users[0], users[0])
            else:
                string += '<option value="%s" selected>%s</option>' % (users[0], users[0])
        string += '</select>'
        session.pop('replyAll', None)
        return string
    elif 'replyOne' in session:
        cursor.execute('SELECT * FROM messagesid WHERE message_id = "%s"' % (messageid))
        info=cursor.fetchall()[0][0]
        for users in data:
            if users[0] != info:
                string += '<option value="%s">%s</option>' % (users[0], users[0])
            else:
                string += '<option value="%s" selected>%s</option>' % (users[0], users[0])
        string += '</select>'
        session.pop('replyOne', None)
        return string
                
    else:
        for users in data:
            string += '<option value="%s">%s</option>' % (users[0], users[0])
        string += '</select>'
        return string
            
    
@app.route('/reply', methods=["GET", "POST"])
def reply():
    session['replyAll'] = request.values['messageid']
    return redirect('/sendmessage')
        
@app.route('/todolist', methods=["POST", "GET"])
def todolist():
    if 'username' in session:
        if request.method == "POST":
            putInTodolist(session['username'], request.form.get('description'))
            flash('Succesfully put into your to do list!')
    return render_template("todolist.html", todostring=takeFromTodolist(session['username']))
        
        
        
def takeFromTodolist(user):
    cursor, conn = cursorcreate()
    string = ''
    cursor.execute('SELECT * FROM todolist WHERE to_do_user ="%s"' % (user))
    data = cursor.fetchall()
    for parts in data:
        string += '<p>%s      <a href="/delete?id=%s">Delete</a>     <a href="/edit?id=%s">Edit</a></p>'%(parts[2],parts[0], parts[0])
        
    return string
        
def putInTodolist(user, to_do):
    cursor, conn = cursorcreate()
    cursor.execute("INSERT INTO todolist(to_do_user, to_do_string) VALUES('%s', '%s')"%(user,to_do))
    conn.commit()
    return None
    
def deleteTodolist(id):
    cursor, conn = cursorcreate()
    
    cursor.execute("DELETE FROM todolist WHERE to_do_id = '%s'" % (id))
    conn.commit()
    return None
    
@app.route('/delete', methods=["GET", "POST"])
def delete():
    deleteTodolist(request.values['id'])
    flash('Succesfully deleted!')
    return redirect('/todolist')

        
@app.route('/edit', methods=["GET", "POST"])
def edit():
    cursor, conn = cursorcreate()
    if request.method == "POST":
        cursor.execute("UPDATE todolist SET to_do_string='%s' WHERE to_do_id = '%s'" % (request.form.get('editedMessage'), request.form.get('messageid')))
        conn.commit()
        flash('Succesfully edited!')
        return redirect('/todolist')
    return render_template("edit.html", originalMessage = editFinder(request.values['id'])[0], messageid = request.values['id'])
        
@app.route('/replyOne', methods=["GET", "POST"])      
def replyOne():
    session['replyOne'] = request.values['messageid']
    return redirect('/sendmessage')
        
        
def editFinder(id):
    cursor, conn = cursorcreate()
    cursor.execute('SELECT to_do_string FROM todolist WHERE to_do_id = "%s"' % (id))
    data = cursor.fetchone()
    return data
    
def cursorcreate():
    MYSQL_DATABASE_HOST = os.getenv('IP', '127.0.0.1')
    MYSQL_DATABASE_USER = 'huanghenry'
    MYSQL_DATABASE_PASSWORD = 'tab3le2U$'
    MYSQL_DATABASE_DB = 'my_flask_app'
    
    conn = pymysql.connect(
        host = MYSQL_DATABASE_HOST,
        user = MYSQL_DATABASE_USER,
        password = MYSQL_DATABASE_PASSWORD,
        db = MYSQL_DATABASE_DB
        )
        
    cursor = conn.cursor()
    return cursor, conn
    
    
    
if __name__ == '__main__':
    host=os.getenv('IP', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    app.debug = True
    app.secret_key = 'PBN\xbb\xae"\xe7\xc6\x98\xe2w\x0fB\xa3\x1e\xa0\x1d6(\xda:Kq\xd7'
    #logging
    handler = RotatingFileHandler('error.log', maxBytes = 10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host=host, port=port)