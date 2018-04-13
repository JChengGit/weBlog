import re,psycopg2
from flask_bootstrap import Bootstrap
from flask import Flask,request,render_template,redirect,make_response,session


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
    return render_template('home.html')

@app.route('/home',methods=['POST'])
def post():
    user_id = session['current']
    content = request.form['content']

    conn = psycopg2.connect(dbname="weibo", user="postgres",
    	password="456", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    data = (user_id,content)
    cur.execute("INSERT INTO posts(user_id,content) values(%s,%s)",data)
    conn.commit()
    conn.close()
    return redirect('/home')
    
@app.route('/login',methods=['GET'])
def logform():
    return render_template('login.html')
    
@app.route('/login',methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    conn = psycopg2.connect(dbname="weibo", user="postgres",
    	password="456", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT password,id FROM users WHERE email=%s",(email,))
    ps = cur.fetchall()
    user_id = ps[0][1]

    if len(ps) == 0:
        return render_template('login.html',message=
            'User does not exist')

    if ps[0][0] == password:
        session['current'] = user_id
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

    if validateEmail(email)==0:
        return render_template('register.html',message=
    		'Please type in a valid Email.')

    if password2!= password:
        return render_template('register.html',message=
            'Please type in same password')

    conn = psycopg2.connect(dbname="weibo", user="postgres",
    	password="456", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    
    cur.execute("select id from users where email=%s",(email,))
    if len(cur.fetchall())!=0:
        return render_template('register.html',message=
            'This Email has been registered.')

    data = (email,name,password,gender)
    cur.execute("INSERT INTO users(email,name,password,gender) VALUES(%s,%s,%s,%s)",data)
    conn.commit()
    conn.close()
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

app.run()



