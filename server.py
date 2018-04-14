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
    email = format_space(email)
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

    email = format_space(email)
    name = format_space(name)

    if name==0:
        return render_template('register.html',message=
            'Please type in an username.')

    if validateEmail(email)==0:
        return render_template('register.html',message=
    		'Please type in a valid Email.')

    if password2!= password:
        return render_template('register.html',message=
            'Please type in same passwords.')

    create_user(email,name,password, gender)
    return redirect('/login')

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

def validateEmail(addr):
    if len(addr) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\."
                    "([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",addr) != None:
            return 1
    return 0

def create_user(email, name, password, gender):
    cur = CONN.cursor()
    cur.execute("select id from users where email=%s",(email,))
    if len(cur.fetchall())!=0:
        return render_template('register.html',message=
            'This Email has been registered.')

    data = (email,name,password,gender)
    cur.execute("INSERT INTO users(email,name,password,gender) VALUES(%s,%s,%s,%s)",data)
    CONN.commit()

def format_space(st):
    if re.match(r'^\s+$',st):
        return(0)
    args = re.split(r'\s+',st)
    length = len(args)
    if len(args[0])==0:
        args.pop(0)
        length=length-1
    if len(args[length-1])==0:
        args.pop(length-1)
        length=length-1
    format_st = args[0]
    i=1
    while i<length:
        format_st = format_st+" "+args[i]
        i = i+1
    return format_st


CONN = psycopg2.connect(dbname="weibo", user="postgres",
        password="456", host="127.0.0.1", port="5432")
app.run()



