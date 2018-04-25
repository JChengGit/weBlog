import re,psycopg2
from flask_bootstrap import Bootstrap
from flask import Flask,request,render_template,redirect,make_response,session

CONN = None
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = b'\xa5`k\xe8H2/\xdf\x17\x18r1\xb1\xd2jB\xf4\x86\xa3.\x02g\x94\x81'

@app.route('/')
def index():
    return redirect('/login')

@app.route('/home',methods=['GET'])
def home(): 
    if 'current' not in session:
        return redirect('/login')

    current_id = session['current']
    cur = CONN.cursor()
    cur.execute("select content,create_at from posts where user_id=%s",(current_id,))
    posts = cur.fetchall()
    length = len(posts)
    cnt = []
    tmstp = []
    for i in posts:
        cnt.append(i[0])
        tmstp.append(i[1])
    return render_template('home.html',postlist=cnt,tmstp=tmstp)

@app.route('/home',methods=['POST'])
def post():
    user_id = session['current']
    content = request.form['content']

    cur = CONN.cursor()
    data = (user_id,content)
    cur.execute("INSERT INTO posts(user_id,content) values(%s,%s)",data)
    CONN.commit()
    return redirect('/home')
    
@app.route('/login',methods=['GET'])
def logform():
    return render_template('login.html')
    
@app.route('/login',methods=['POST'])
def login():
    email = request.form['email']
    email = format_str(email)
    password = request.form['password']
    
    cur = CONN.cursor()
    cur.execute("SELECT password,id FROM users WHERE email=%s",(email,))
    info = cur.fetchall()

    if len(info) == 0:
        return render_template('login.html',message=
            'User does not exist')

    if info[0][0] == password:
        session['current'] = info[0][1]
        return redirect('/home')
    return render_template('login.html',message=
        'Invalid email or password')
    
@app.route('/register',methods=['GET'])
def regiform():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    password2 = request.form['password2']
    gender = int(request.form['gender'])

    email = format_str(email)
    name = format_str(name)

    if validate_email(email)==0:
        return render_template('register.html',message='Please type in a valid Email.')
    if password2!= password:
        return render_template('register.html',message='Please type in same passwords.')

    result = create_user(email,name,password,gender)
    if result == "users_name_key":
        return render_template('register.html',message="Username has already existed.")
    elif result == "users_email_key":
        return render_template('register.html',message="Email has already been registered.")
    else:
        return redirect('/login')



@app.route('/setting',methods = ['GET'])
def setting():
    return render_template('setting.html')
@app.route('/setting',methods = ['POST'])
def reset():
    current_id = session['current']
    cur = CONN.cursor()
    try:
        usn = format_str(request.form['username'])
        if usn == 0:
            return render_template('setting.html',usn="Please type in an username.")
        username = "'"+usn+"'"
        try:
            cur.execute("UPDATE users SET name={} WHERE id={}".format(username,current_id))
        except psycopg2.IntegrityError as e:
            err = e.args[0].split('"')[1]
            if  err == "users_name_key":
                CONN.commit()
                return render_template('setting.html',usn="Username has already existed.")
            return 'Unknown Error.'
        CONN.commit()
        return render_template('setting.html',usn="You have changed your username into {}.".format(usn))
    except:
        password = request.form['password']
        password2 = request.form['password2']
        if password2 != password:
            return render_template('/setting',pwd="Please type in same passwords.")
        cur.execute("UPDATE users SET password={} WHERE id={}".format(password,current_id))
        CONN.commit()
        return render_template('setting.html',pwd="You have changed your password.")



@app.route('/find')
def find():
    return render_template('find.html')

@app.route('/favorates')
def favorates():
    return render_template('favorates.html')

@app.route('/follow')
def follow():
    return render_template('follow.html') 

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('current',None)
    return redirect('/login')



def validate_email(addr):
    if len(addr) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\."
                    "([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",addr) != None:
            return 1
    return 0

def create_user(email, name, password, gender):
    cur = CONN.cursor()
    data = (email,name,password,gender)
    try:
        cur.execute("INSERT INTO users(email,name,password,gender) VALUES(%s,%s,%s,%s)",data)
        CONN.commit()
    except  psycopg2.IntegrityError as e:
        err = e.args[0].split('"')[1]
        CONN.commit()
        return err


def format_str(st):
    if re.match(r'^\s+$',st):
        return 0
    format_st = re.sub(r'\s+',r' ',st.strip()).lower()
    return format_st


CONN = psycopg2.connect(dbname="weibo", user="postgres",
        password="456", host="127.0.0.1", port="5432")


if __name__ == '__main__':
    app.run()

