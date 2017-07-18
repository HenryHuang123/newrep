import os
import time
import datetime
import pytz

from flask import Flask, url_for, request, render_template, redirect, flash, make_response, session
import logging
import pymysql
from logging.handlers import RotatingFileHandler
app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if validLogin(request.form['username'], request.form['password']) == True:
            flash('Succesfully logged in')
            session['username']=request.form.get('username')
            return redirect(url_for('welcome'))
        else:
            error = 'Incorrect username and password.'
            app.logger.warning("Incorrect username and password for user (%s)", request.form.get('username'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
    
@app.route('/deleteMail')
def deleteMail():
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
    cursor.execute('DELETE FROM messagesid WHERE message_id = "%s" and to_user = "%s"'%(request.values['messageid'], session['username']))
    conn.commit()
    flash('Message deleted!')
    return redirect('/')
    
    
@app.route('/')
def welcome():
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
    
    if 'username' in session:
        cursor.execute('SELECT * FROM messagesid WHERE to_user="%s"' % session['username'])
        data = cursor.fetchall()
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
    invalid_character_array = ["{", "[", "}", "]", "-", "_", "=", "+", "~", "`", " ", "'", "\""]
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
        
    if any(x in username for x in invalid_character_array):
        return False
    elif any(x in password for x in invalid_character_array):
        return False
    elif password == '' or username =='':
        return False
    else:
        cursor = conn.cursor()
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
    if request.method == "POST":
        if any(x in request.form.get('username') for x in invalid_character_array):
            error = "Invalid character in username!"
        elif any(x in request.form.get('password') for x in invalid_character_array):
            error = "Invalid character in password!"
        else:
            if request.form.get('password') == request.form.get('confirm') and request.form.get('username') != '' and request.form.get('password') != '' and 64 >= len(request.form.get('username')) >= 6 and 64 >= len(request.form.get('password')) >= 6:
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
                cursor.execute("insert into user(username, password) values('%s', '%s');" % (request.form.get('username'), request.form.get('password')))
                conn.commit()
                session['username']=request.form.get('username')
                return redirect(url_for('welcome'))
            
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
            info = request.form.getlist('toUser')
            cursor.execute("insert into messages(message, datetime) values('%s', '%s');" % (request.form.get('message'), string))
            conn.commit()
            for i in range(0, len(info)):
                databaseURL(request.form.get('message'), info[i], session['username'])
            flash('Succesfully sent your message!')
            return redirect(url_for('welcome'))
    else:
        return redirect(url_for('login'))
        
    return render_template('postlink.html', error=error, multiselect=multiselect)
    
@app.route('/sentmail')
def sentmail():
    if 'username' in session:
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
    error = None
    cursor.execute('SELECT message_id FROM messages WHERE message="%s"'%(message))
    number = cursor.fetchall()[-1]
    cursor.execute('INSERT INTO messagesid VALUES("%s", "%s", "%s")'%(sendingUser, user, number[0]))
    conn.commit()
    return error
    
    
        
        
def convert_multi_select():
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
    cursor.execute('SELECT username FROM user')
    data = cursor.fetchall()
    string = "<select multiple id='multiselect' name='toUser'>"
    
    for users in data:
        string += '<option value="%s">%s</option>' % (users[0], users[0])
    string += '</select>'
    return string
    
    
def convert_multi_select_reply(messageid):
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
    string = ''
    cursor.execute('SELECT * FROM todolist WHERE to_do_user ="%s"' % (user))
    data = cursor.fetchall()
    for parts in data:
        string += '<p>%s      <a href="/delete?id=%s">Delete</a>     <a href="/edit?id=%s">Edit</a></p>'%(parts[2],parts[0], parts[0])
        
    return string
        
def putInTodolist(user, to_do):
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
    cursor.execute("INSERT INTO todolist VALUES('', '%s', '%s')"%(user,to_do))
    conn.commit()
    return None
    
def deleteTodolist(id):
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
    cursor.execute('SELECT to_do_string FROM todolist WHERE to_do_id = "%s"' % (id))
    data = cursor.fetchone()
    return data
    
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
    
    

#hi    
