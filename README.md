1. How to install and run

1) create database:
		createdb weibo
		psql weibo
		\i tables.sql
2) run
	unzip the source code and:
		pip install –r requirements.txt
		python server.py
	OR use docker:
		docker build –t weibo .
		docker run –net==host weibo 
	Open the link 127.0.0.1:5000 to visit


2. Source Code Document

1) Date base
	Connect the database through python psycopg
	Keep the sql lines in tables.sql，quick to create database
	Using the trigger to count number of posts,comments,likes etc. and deal with associate deleting
	database structure is displayed in schema.jpg

2) About server.py
	/register  			for registration
	Call create_user() to register via e-mail and username
	Call validate_email() to verify if the e-mail is legal
	Using MD5 hash the users’ password.

	/login  			for login
	Call user_login() to login
	Using session to keep user login status and store user's id

	/find & /follow 	for browse people who using the weibo, and follow/unfollow them
	/setting 			for changing password and delete user account

	/community  		for homepage
	Display the posts comments and likes of user him/herself and people he/she followed by sql search.
	Using textarea to type in the content of post

	/post 				for write the post info into db
	/post/like			for write the like info into db
	/post/update 		for update the post info in db
	/post/delete 		for delete the post info in db

	/comment 			for write the comment info into db
	/comment/like 		for write the comment like info into db
	/comment/update 	for update the comment info in db
	/comment/delete 	for delete the comment info in db

3) UI
	Design the webpage by using HTML/CSS/JavaScript
	Using AJAX to implement the interact of like action
	Display the webpage via flask framework render_template()
	HTML files placed in templates/
	CSS files placed in static/

4) Unittest
	serverCopy.py is the copy of the server.py, but serverCopy.py connect to testdb.
	to do the unittest :
		createdb testdb
		psql testdb
		\i tables.sql
		\q
		python serverTest.py



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
