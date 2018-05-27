import re,psycopg2,hashlib
from flask import Flask,request,render_template,redirect,make_response,session,flash

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
    p_message = request.args.get('ms')
    if p_message == "pf":
        p_message = "Please type in your post."
    if p_message == "uf":
        p_message = "Update failed, please type in your post."
    if p_message == "cf":
        p_message = "Update failed, please type in your comment."
    try:
        cur = CONN.cursor()
        cur.execute("SELECT u.name,u.id,p.id,p.content,p.liked,p.commented,p.create_at \
            FROM users u, posts p, follows f \
            WHERE f.fan_id=%s AND u.id=f.user_id AND p.user_id=u.id \
            UNION SELECT u.name,u.id,p.id,p.content,p.liked,p.commented,p.create_at \
            FROM users u, posts p WHERE u.id=%s AND p.user_id=u.id \
            ORDER BY create_at;",(current_id,current_id))
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    postlist_t = cur.fetchall()
    postlist_t.reverse()
    postlist = []
    for i in postlist_t:
        post = list(i)
        post_id = post[2]
        cur.execute("SELECT u.id,u.name,c.id,c.content,c.liked,c.create_at \
            FROM users u, comments c WHERE c.post_id=%s AND u.id=c.user_id \
            ORDER BY create_at;",(post_id,))
        comments = cur.fetchall()
        comments.reverse()
        post.append(comments)
        postlist.append(post)
    cur.execute("SELECT name,email,posts FROM users WHERE id=%s",(current_id,))
    userinfo = cur.fetchall()[0]
    return render_template('community.html',postlist=postlist,userinfo=userinfo,
        current_id=current_id,p_message=p_message)


@app.route('/post',methods=['POST'])
def post():
    current_id = session['current']
    content = request.form['content']
    try:
        result = create_post(current_id,content)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == 'post failed':
        return redirect('/community?ms=pf')
    return redirect('/community')
@app.route('/post/like',methods=['GET'])
def likepost():
    current_id = session['current']
    post_id = int(request.args.get('post_id'))
    try:
        return like_post(current_id,post_id)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
@app.route('/post/update',methods=['POST'])
def updatepost():
    post_id = request.form['post_id']
    content = request.form['uptxt']
    try:
        result = update_post(post_id,content)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == 'update failed':
        return redirect('/community?ms=uf')
    return redirect('/community')
@app.route('/post/delete',methods=['POST'])
def delete_post():
    try:
        cur = CONN.cursor()
        post_id = request.form['post_id']
        cur.execute("DELETE FROM posts WHERE id=%s",(post_id,))
        CONN.commit()
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return redirect('/community')


@app.route('/comment',methods=['POST'])
def comment():
    current_id = session['current']
    post_id = request.form['post_id']
    content = format_space(request.form['content'])
    try:
        result = create_comment(current_id,post_id,content)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == "comment failed":
        return redirect('/community?ms=cf')
    return redirect('/community')
@app.route('/comment/like',methods=['GET'])
def likecomment():
    current_id = session['current']
    comment_id = request.args.get('comment_id')
    try:
        return like_comment(current_id,comment_id)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
@app.route('/comment/update',methods=['POST'])
def updatecomment():
    comment_id = request.form['comment_id']
    content = request.form['upcmt']
    try:
        result = update_comment(comment_id,content)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == 'update failed':
        return redirect('/community?ms=cf')
    return redirect('/community')
@app.route('/comment/delete',methods=['POST'])
def delete_comment():
    try:
        cur = CONN.cursor()
        comment_id = request.form['comment_id']
        cur.execute("DELETE FROM comments WHERE id=%s",(comment_id,))
        CONN.commit()
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return redirect('/community')


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
@app.route('/logout',methods=['GET'])
def logout():
    session.pop('current',None)
    return redirect('/login')


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
    if request.args.get('ms')=='wp':
        return render_template('setting.html',message2='Wrong password.')
    return render_template('setting.html')
@app.route('/setting',methods = ['POST'])
def reset():
    current_id = session['current']
    password = request.form['password']
    password2 = request.form['password2']
    try:
        result = change_password(current_id,password,password2)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == 'short':
        return render_template('setting.html',pwd="Password has to be at least 6 characters.")
    if result == 'wrongPWD':
        return render_template('setting.html',pwd="Please type in same passwords.")
    if result == 'notPWD':
        return render_template('setting.html',pwd="Only letters or numbers are allowed.")
    if result == 'samePWD':
        return render_template('setting.html',pwd="Same as previous password.")
    return render_template('setting.html',pwd="You have changed your password.")
@app.route('/setting/cancellation',methods=['POST'])
def cancellation():
    current_id = session['current']
    password = request.form['password']
    try:
        result = delete_user(current_id,password)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    if result == 1:
        return redirect('/login')
    else:
        return redirect('/setting?ms=wp')


@app.route('/find',methods=['GET'])
def find():
    if 'current' not in session:
        return redirect('/login')
    current_id = session['current']
    try:
        cur = CONN.cursor()
        cur.execute("SELECT id,name,gender,email FROM users WHERE id!=%s \
            AND id NOT IN (SELECT user_id FROM follows \
            WHERE fan_id=%s)",(current_id,current_id))
        data = cur.fetchall()
        CONN.commit()
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return render_template('find.html',users=data)
@app.route('/find',methods=['POST'])
def found():
    current_id = session['current']
    user_id = request.form['user_id']
    try:
        follow_user(current_id,user_id)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return redirect('/find')


@app.route('/follow',methods=['GET'])
def follow():
    if 'current' not in session:
        return redirect('/login')
    try:
        cur = CONN.cursor()
        current_id = session['current']
        cur.execute("SELECT followings,followers FROM users WHERE id=%s",(current_id,))
        count = cur.fetchall()[0]
        cur.execute("SELECT id,name,gender,email FROM users WHERE id IN (SELECT user_id FROM follows WHERE fan_id=%s)",(current_id,))
        followings = cur.fetchall()
        cur.execute("SELECT id,name,gender,email FROM users WHERE id IN (SELECT fan_id FROM follows WHERE user_id=%s)",(current_id,))
        followers = cur.fetchall()
        CONN.commit()
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return render_template('follow.html',count=count,followings=followings,followers=followers)
@app.route('/follow',methods=['POST'])
def unfollow():
    current_id = session['current']
    user_id = request.form['user_id']
    try:
        unfollow_user(current_id,user_id)
    except psycopg2.OperationalError as e:
        return render_template('error.html')
    except psycopg2.InterfaceError as e:
        return render_template('error.html')
    return redirect('/follow')


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

def delete_user(current_id,password):
    cur = CONN.cursor()
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    cur.execute("SELECT password FROM users WHERE id=%s",(current_id,))
    pwd = cur.fetchall()[0][0]
    if password_hash == pwd:
        cur.execute("DELETE FROM users WHERE id=%s",(current_id,))
        CONN.commit()
        return 1
    else:
        CONN.commit()
        return 'wrongPWD'

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

def follow_user(current_id,user_id):
    cur = CONN.cursor()
    data = [user_id,current_id]
    cur.execute("INSERT INTO follows(user_id,fan_id) VALUES(%s,%s)",data)
    CONN.commit()

def unfollow_user(current_id,user_id):
    cur = CONN.cursor()
    data = [user_id,current_id]
    cur.execute("DELETE FROM follows WHERE user_id=%s AND fan_id=%s",data)
    CONN.commit()

def create_post(current_id,content):
    content_f = format_space(content)
    cur = CONN.cursor()
    if (content_f == 0) or (content_f == ""):
        CONN.commit()
        return 'post failed'
    data = (current_id,content_f)
    cur.execute("INSERT INTO posts(user_id,content) values(%s,%s)",data)
    CONN.commit()
    return 1

def like_post(current_id,post_id):
    cur = CONN.cursor()
    data = [current_id,post_id]
    cur.execute("SELECT * FROM likeposts WHERE user_id=%s AND post_id=%s",data)
    if len(cur.fetchall())==0:
        cur.execute("INSERT INTO likeposts values(%s,%s)",data)
    else:
        cur.execute("DELETE FROM likeposts WHERE user_id=%s AND post_id=%s",data)
    cur.execute("SELECT liked FROM posts WHERE id=%s",(post_id,))
    liked = cur.fetchall()[0][0]
    CONN.commit()
    return str(liked)

def update_post(post_id,content):
    cur = CONN.cursor()
    content_f = format_space(content)
    if (content_f == 0) or (content_f == ""):
        return 'update failed'
    data = [content_f,post_id]
    cur.execute("UPDATE posts SET content=%s WHERE id=%s",data)
    CONN.commit()
    return 1

def create_comment(current_id,post_id,content):
    cur = CONN.cursor()
    content_f = format_space(content)
    if (content_f == 0) or (content_f == ""):
        return "comment failed"
    data = [current_id,post_id,content_f]
    cur.execute("INSERT INTO comments(user_id,post_id,content) VALUES(%s,%s,%s)",data)
    CONN.commit()
    return 1

def  like_comment(current_id,comment_id):
    cur = CONN.cursor()
    data = [current_id,comment_id]
    cur.execute("SELECT * FROM likecmts WHERE user_id=%s AND comment_id=%s",data)
    if len(cur.fetchall())==0:
        cur.execute("INSERT INTO likecmts values(%s,%s)",data)
    else:
        cur.execute("DELETE FROM likecmts WHERE user_id=%s AND comment_id=%s",data)
    cur.execute("SELECT liked FROM comments WHERE id=%s",(comment_id,))
    liked = cur.fetchall()[0][0]
    CONN.commit()
    return str(liked)

def update_comment(comment_id,content):
    cur = CONN.cursor()
    content_f = format_space(content)
    if (content_f == 0) or (content_f == ""):
        return 'update failed'
    data = [content_f,comment_id]
    cur.execute("UPDATE comments SET content=%s WHERE id=%s",data)
    CONN.commit()
    return 1

def change_password(current_id,password,password2):
    cur = CONN.cursor()
    cur.execute("SELECT password FROM users WHERE id=%s",(current_id,))
    originPWD = cur.fetchall()[0][0]
    password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
    if len(password) < 6:
        return 'short'
    if password2 != password:
        return 'wrongPWD'
    if not(re.match(r'^[a-zA-Z0-9]+$',password)):
        return 'notPWD'
    if password_hash == originPWD:
        return 'samePWD'
    cur.execute("UPDATE users SET password=%s WHERE id=%s",(password_hash,int(current_id)))
    CONN.commit()
    return 1

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