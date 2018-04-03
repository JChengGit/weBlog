import re,psycopg2
from flask_bootstrap import Bootstrap
from flask import Flask,request,render_template,redirect,make_response,session


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = b'\xa5`k\xe8H2/\xdf\x17\x18r1\xb1\xd2jB\xf4\x86\xa3.\x02g\x94\x81'

@app.route('/')
def index():
	return redirect('login')

@app.route('/home')
def home():
    if 'current' not in session:
        return redirect('/login')
    return 'login!'
    
@app.route('/login',methods=['GET'])
def logform():
    return render_template('login.html')
    
@app.route('/login',methods=['POST'])
def login():
    name = request.form['name']
    password = int(request.form['password'])
    
    conn = psycopg2.connect(dbname="weibo", user="postgres",password="456", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE name=%s",(name,))
    ps = cur.fetchall()

    if len(ps) == 0:
        return render_template('login.html',message=
            'User does not exist')

    print(type(ps[0][0]),type(password))

    if ps[0][0] == password:
        session['current'] = name
        return redirect('/home')
    return render_template('login.html',message=
        'Invalid email or password')
    
@app.route('/register',methods=['GET'])
def regiform():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register():
    name = request.form['name']
    password = request.form['password']
    password2 = request.form['password2']
    age = request.form['age']
    conn = psycopg2.connect(dbname="weibo", user="postgres",password="456", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    
    cur.execute("select id from users where name=%s",(name,))
    if len(cur.fetchall())!=0:
        return render_template('register.html',message=
            'username has already exist.')

    if password2!= password:
        return render_template('register.html',message=
            'Please type in same password')

    data = (name,password,age)
    cur.execute('insert into users(name,password,age) values(%s,%s,%s)',data)
    conn.commit()
    conn.close()
    return redirect('/login')

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

app.run(port=3000)



