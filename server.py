import re,psycopg2,hashlib
from flask import Flask,request,render_template,redirect,make_response,session

CONN = None
app = Flask(__name__)
app.secret_key = b'\xa5`k\xe8H2/\xdf\x17\x18r1\xb1\xd2jB\xf4\x86\xa3.\x02g\x94\x81'

@app.route('/')
def index():
    return redirect('/login')


@app.route('/community',methods=['GET'])
def view():
    if 'current' not in session:
        return redirect('/login')
    current_id = session['current']
    cur = CONN.cursor()
    cur.execute("SELECT distinct(u.name),p.content,p.create_at FROM users u, posts p, follows f WHERE f.fan_id=%s AND (u.id=f.user_id or u.id=%s) AND p.user_id=u.id;",(current_id,current_id))
    postlist = cur.fetchall()
    postlist.reverse()
    cur.execute("SELECT name,email FROM users WHERE id=%s",(current_id,))
    userinfo = cur.fetchall()[0]
    return render_template('community.html',postlist=postlist,userinfo=userinfo)
@app.route('/community',methods=['POST'])
def commu():


    return render_template('community.html',postlist=postlist,userinfo=userinfo)



@app.route('/home',methods=['GET'])
def home(): 
    if 'current' not in session:
        return redirect('/login')
    current_id = session['current']
    cur = CONN.cursor()
    cur.execute("SELECT name,posts,email FROM users WHERE id=%s",(current_id,))
    userinfo = cur.fetchall()[0]
    username = userinfo[0]
    post_number = userinfo[1]
    email = userinfo[2]
    cur.execute("SELECT id,content,create_at FROM posts WHERE user_id=%s",(current_id,))
    posts = cur.fetchall()
    posts.reverse()
    return render_template('home.html',username=username,post_number=post_number,
        posts=posts,email=email)
@app.route('/home',methods=['POST'])
def post():
    cur = CONN.cursor()
    current_id = session['current']
    content = format_space(request.form['content'])
    if (content == 0) or (content == ""):
        cur.execute("SELECT name,posts,email FROM users WHERE id=%s",(current_id,))
        userinfo = cur.fetchall()[0]
        username = userinfo[0]
        post_number = userinfo[1]
        email = userinfo[2]
        cur.execute("SELECT content,create_at FROM posts WHERE user_id=%s",(current_id,))
        posts = cur.fetchall()
        posts.reverse()
        return render_template('home.html',username=username,post_number=post_number,
            posts=posts,email=email,message='Please type in your post.')
        cur = CONN.cursor()
    data = (current_id,content)
    cur.execute("INSERT INTO posts(user_id,content) values(%s,%s)",data)
    CONN.commit()
    return redirect('/home')


@app.route('/post/<post_id>',methods=['GET'])
def delete_post(post_id):
    if 'current' not in session:
        return redirect('/login')
    cur = CONN.cursor()
    cur.execute("DELETE FROM posts WHERE id=%s",(post_id,))
    return redirect('/home')



@app.route('/login',methods=['GET'])
def logform():
    return render_template('login.html')
@app.route('/login',methods=['POST'])
def login():
    password = request.form['password']
    name = request.form['name']
    result = user_login(name,password)
    if result == "space":
        return render_template('login.html',message='Please type in Email or username.')
    if result == "noName":
        return render_template('login.html',message='User does not exist.')
    if result == "wrongPWD":
        return render_template('login.html',message='Invalid password.')
    else:
        session['current'] = result
        return redirect('/community')


@app.route('/register',methods=['GET'])
def regiform():
    return render_template('register.html')
@app.route('/register',methods=['POST'])
def register():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    password2 = request.form['password2']
    gender = request.form['gender']
    result = create_user(email,name,password,password2,gender)
    if result == 'invalidEmail':
        return render_template('register.html',message='Please type in a valid Email.')
    if result == 'noName':
        return render_template('register.html',message='Please type in a Username.')
    if result == 'short':
        return render_template('register.html',message='Password has to be at least 6 characters.')
    if result == 'wrongPWD':
        return render_template('register.html',message='Please type in same passwords.')
    if result == 'wrongType':
    	return render_template('register.html',message="Only letters or numbers are allowed to be password.")
    if result == "users_name_key":
        return render_template('register.html',message="Username has already existed.")
    if result == "users_email_key":
        return render_template('register.html',message="Email has already been registered.")
    else:
        return redirect('/login')


@app.route('/setting',methods = ['GET'])
def setting():
    if 'current' not in session:
        return redirect('/login')
    return render_template('setting.html')
@app.route('/setting',methods = ['POST'])
def reset():
    current_id = session['current']
    cur = CONN.cursor()
    cur.execute("SELECT password FROM users WHERE id=%s",(current_id,))
    originPWD = cur.fetchall()[0][0]
    password = request.form['password']
    password2 = request.form['password2']
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    if len(password) < 6:
        return render_template('setting.html',pwd="Password has to be at least 6 characters.")
    if password2 != password:
        return render_template('setting.html',pwd="Please type in same passwords.")
    if not(re.match(r'^[a-zA-Z0-9]+$',password)):
    	return render_template('setting.html',
    		pwd="Only letters or numbers are allowed.") 
    if password_hash == originPWD:
        return render_template('setting.html',pwd="Same as previous password.")
    cur.execute("UPDATE users SET password=%s WHERE id=%s",(password,int(current_id)))
    CONN.commit()
    return render_template('setting.html',pwd="You have changed your password.")


@app.route('/find',methods=['GET'])
def find():
    if 'current' not in session:
        return redirect('/login')
    current_id = session['current']
    cur = CONN.cursor()
    cur.execute("SELECT id,name,gender,email FROM users WHERE id!=%s AND id NOT IN (SELECT user_id FROM follows WHERE fan_id=%s)",(current_id,current_id))
    data = cur.fetchall()
    CONN.commit()
    return render_template('find.html',users=data)
@app.route('/find',methods=['POST'])
def found():
    current_id = session['current']
    user_id = request.form['user_id']
    cur = CONN.cursor()
    data = [user_id,current_id]
    cur.execute("INSERT INTO follows(user_id,fan_id) VALUES(%s,%s)",data)
    CONN.commit()
    return redirect('/find')


@app.route('/follow',methods=['GET'])
def follow():
    if 'current' not in session:
        return redirect('/login')
    cur = CONN.cursor()
    current_id = session['current']
    cur.execute("SELECT followings,followers FROM users WHERE id=%s",(current_id,))
    count = cur.fetchall()[0]
    cur.execute("SELECT id,name,gender,email FROM users WHERE id IN (SELECT user_id FROM follows WHERE fan_id=%s)",(current_id,))
    followings = cur.fetchall()
    cur.execute("SELECT id,name,gender,email FROM users WHERE id IN (SELECT fan_id FROM follows WHERE user_id=%s)",(current_id,))
    followers = cur.fetchall()
    CONN.commit()
    return render_template('follow.html',count=count,followings=followings,followers=followers)
@app.route('/follow',methods=['POST'])
def unfollow():
    cur = CONN.cursor()
    current_id = session['current']
    user_id = request.form['user_id']
    data = [user_id,current_id]
    cur.execute("DELETE FROM follows WHERE user_id=%s AND fan_id=%s",data)
    return redirect('/follow')



@app.route('/favorates')
def favorates():
    if 'current' not in session:
        return redirect('/login')
    return render_template('favorates.html')
@app.route('/logout',methods=['GET'])
def logout():
    session.pop('current',None)
    return redirect('/login')


def create_user(email, name, password, password2, gender):
    email = format_space(email)
    name = format_space(name)
    if email==0:
        return 'invalidEmail'
    if validate_email(email)==0:
        return 'invalidEmail'
    if name==0:
        return 'noName'
    if len(password)<6:
        return 'short'
    if password != password2:
        return 'wrongPWD'
    if not(re.match(r'^[a-zA-Z0-9]+$',password)):
    	return 'wrongType'
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    cur = CONN.cursor()
    data = [email.lower(),name,password_hash,gender]
    try:
        cur.execute("INSERT INTO users(email,name,password,gender) VALUES(%s,%s,%s,%s)",data)
        CONN.commit()
    except  psycopg2.IntegrityError as e:
        result = e.args[0].split('"')[1]
        CONN.commit()
        return result

def user_login(name,password):
    cur = CONN.cursor()
    name_f = format_space(name)
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    if name_f == 0:
    	return "space"
    if validate_email(name_f)==1:
        cur.execute("SELECT password,id FROM users WHERE email=%s",(name_f.lower(),))
    else:
        cur.execute("SELECT password,id FROM users WHERE name=%s",(name_f,))
    info = cur.fetchall()
    if len(info) == 0:
        return "noName"
    elif info[0][0] != password_hash:
        return "wrongPWD"
    else:
        return info[0][1]

def format_space(st):
    if re.match(r'^\s+$',st):
        return 0
    format_st = re.sub(r'\s+',r' ',st.strip())
    return format_st

def validate_email(addr):
    if len(addr) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\."
                    "([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",addr) != None:
            return 1
    return 0


CONN = psycopg2.connect(dbname="weibo", user="postgres",
    password="456", host="127.0.0.1", port="5432")
if __name__ == '__main__':
    app.run()