<h3>1. How to install and run</h3>
<hr>
1) create database:<br>
		&nbsp;createdb weibo<br>
		&nbsp;psql weibo<br>
		&nbsp;\i tables.sql<br>
2) run<br>
	unzip the source code and:<br>
		&nbsp;pip install –r requirements.txt<br>
		&nbsp;python server.py<br>
	OR use docker:<br>
		&nbsp;docker build –t weibo .<br>
		&nbsp;docker run –net==host weibo <br>
	Open the link 127.0.0.1:5000 to visit<br>
<br>

<h3>2. Source Code Document</h3>
<hr>
1) Date base<br>
	Connect the database through python psycopg<br>
	Keep the sql lines in tables.sql，quick to create database<br>
	Using the trigger to count number of posts,comments,likes etc. and deal with associate deleting<br>
	database structure is displayed in schema.jpg<br>

2) About server.py<br>
	/register  			for registration<br>
	Call create_user() to register via e-mail and username<br>
	Call validate_email() to verify if the e-mail is legal<br>
	Using MD5 hash the users’ password.<br>
<br>
	/login  			for login<br>
	Call user_login() to login<br>
	Using session to keep user login status and store user's id<br>
<br>
	/find & /follow 	for browse people who using the weibo, and follow/unfollow them<br>
	/setting 			for changing password and delete user account<br>
<br>
	/community  		for homepage<br>
	Display the posts comments and likes of user him/herself and people he/she followed by sql search.<br>
	Using textarea to type in the content of post<br>
<br>
	/post 				for write the post info into db<br>
	/post/like			for write the like info into db<br>
	/post/update 		for update the post info in db<br>
	/post/delete 		for delete the post info in db<br>
<br>
	/comment 			for write the comment info into db<br>
	/comment/like 		for write the comment like info into db<br>
	/comment/update 	for update the comment info in db<br>
	/comment/delete 	for delete the comment info in db<br>


3) UI<br>
	Design the webpage by using HTML/CSS/JavaScript<br>
	Using AJAX to implement the interact of like action<br>
	Display the webpage via flask framework render_template()<br>
	HTML files placed in templates/<br>
	CSS files placed in static/<br>

4) Unittest<br>
	serverCopy.py is the copy of the server.py, but serverCopy.py connect to testdb.<br>
	to do the unittest :<br>
		&nbsp;createdb testdb<br>
		&nbsp;psql testdb<br>
		&nbsp;\i tables.sql<br>
		&nbsp;\q<br>
		&nbsp;&nbsp;python serverTestpy<br>
<br><br><br><br>

<h2>进度</h2>
在127.0.0.1:5000中运行，会自动转到注册界面；<br>
在/login中登录，在/register中注册，使用邮箱注册；<br>
<br>
4.13更新<br>
导航栏，初步的post功能；<br>
<br>
4.14更新<br>
空格处理；<br>
可用邮箱或用户名登录。<br>
<br>
4.27更新<br>
在/setting中改密码；<br>
在/post中用trigger计数；<br>
unittest部分。<br>
<br>
5.3更新<br>
一些细节处理。<br>
<br>
5.4更新<br>
follow、unfollow功能及其计数；<br>
修改tables.sql中的bug，重建数据库；<br>
弃用Bootstrap模板，改用原生CSS实现。<br>
<br>
5.6更新<br>
前端调整。<br>
<br>
5.8更新<br>
增加community页面，查看自己和关注者的post；<br>
<br>
5.10更新<br>
数据库增加trigger给点赞计数。<br>
<br>
5.11更新<br>
点赞，使用Ajax以避免刷新整个页面；<br>
修改和删除post；<br>
数据库增加级联删除。<br>
<br>
5.12更新<br>
增加数据库关于评论计数及评论点赞计数的trigger；<br>
增加后端评论，删除评论，评论点赞的逻辑；<br>
<br>
5.18更新<br>
数据库更新，关联删除。<br>
5.19更新<br>
community与home页面合并<br>
评论的发表，计数，点赞，取消赞，赞计数；<br>
评论的删除、更新，及其权限判断；<br>
post和user的关联删除；<br>
注销帐号。<br>
<br>
5.21更新<br>
修复当没有关注关系时不显示post的bug。<br>
5.26更新<br>
扩写unittest内容，server.py和serverCopy.py大量修改。<br>
<br>
