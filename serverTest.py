import unittest
from serverCopy import *

class TestServer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        cur = CONN.cursor()
        create_user("ann@qwe.com","Ann","123123","123123","Female")
        create_user("ben@qwe.com","Ben","123123","123123","Male")
        create_user("carl@qwe.com","Carl","123123","123123","Male")
        cur.execute("UPDATE users SET id=1 WHERE name='Ann'")
        cur.execute("UPDATE users SET id=2 WHERE name='Ben'")
        cur.execute("UPDATE users SET id=3 WHERE name='Carl'")
        create_post(1,"test post origin.")
        cur.execute("UPDATE posts SET id=1 WHERE user_id=1")
        create_comment(1,1,"test comment origin.")
        cur.execute("UPDATE comments SET id=1 WHERE user_id=1")
        follow_user(1,3)
        CONN.commit()

    @classmethod
    def tearDownClass(self):
        cur = CONN.cursor()
        cur.execute("DELETE FROM users;")
        cur.execute("DELETE FROM posts;")
        cur.execute("DELETE FROM comments;")
        cur.execute("DELETE FROM follows;")
        cur.execute("DELETE FROM likeposts;")
        cur.execute("DELETE FROM likecmts;")
        CONN.commit()
        CONN.close()

    def test_format_space(self):
        st1 = "                   "
        st2 = "   Email           "
        st3 = "   John    Titor   "
        self.assertEqual(format_space(st1),0)
        self.assertEqual(format_space(st2),"Email")
        self.assertEqual(format_space(st3),"John Titor")

    def test_validate_email(self):
        email1 = "123@bjtu.edu.cn"
        email2 = "gmail@.com"
        email3 = "John Titor"
        self.assertEqual(validate_email(email1),1)
        self.assertEqual(validate_email(email2),0)
        self.assertEqual(validate_email(email3),0)

    def test_create_user(self):
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123123","123123","Male"),None)
        self.assertEqual(create_user("invalidEmail","Foo Bar","123123","123123","Male"),"invalidEmail")
        self.assertEqual(create_user("           ","XXX Bar","123123","123123","Male"),"invalidEmail")
        self.assertEqual(create_user("123@qwe.com","         ","123123","123123","Male"),"noName")
        self.assertEqual(create_user("000@qwe.com","XXX Bar","123","123","Male"),"short")
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123123","999999","Male"),"wrongPWD")
        self.assertEqual(create_user("123@qwe.com","Foo Bar","12  12","12  12","Male"),"wrongType")
        self.assertEqual(create_user("123@qwe.com","XXX","999999","999999","Male"),"users_email_key")
        self.assertEqual(create_user("456@qwe.com","Foo Bar","123123","123123","Male"),"users_name_key")

    def test_delete_user(self):
        self.assertEqual(delete_user(2,"111111"),'wrongPWD')
        self.assertEqual(delete_user(2,"123123"),1)

    def test_user_login(self):
        self.assertIsInstance(user_login("123@qwe.com","123123"),int)
        self.assertIsInstance(user_login("    Foo    Bar   ","123123"),int)
        self.assertEqual(user_login("       ","123123"),"space")
        self.assertEqual(user_login("No Name","123123"),"noName")
        self.assertEqual(user_login("123@qwe.com","999999"),"wrongPWD")

    def test_follow_user(self):
        follow_user(3,1)
        cur = CONN.cursor()
        cur.execute("SELECT followers FROM users WHERE id=1")
        followers = cur.fetchall()[0][0]
        cur.execute("SELECT followings FROM users WHERE id=3")
        followings = cur.fetchall()[0][0]
        CONN.commit()
        self.assertEqual(followers,1)
        self.assertEqual(followings,1)

    def test_unfollow_user(self):
        unfollow_user(1,3)
        cur = CONN.cursor()
        cur.execute("SELECT followers FROM users WHERE id=3")
        followers = cur.fetchall()[0][0]
        cur.execute("SELECT followings FROM users WHERE id=1")
        followings = cur.fetchall()[0][0]
        CONN.commit()
        self.assertEqual(followers,0)
        self.assertEqual(followings,0)

    def test_create_post(self):
        self.assertEqual(create_post(1,""),'post failed')
        self.assertEqual(create_post(1,"       "),'post failed')
        self.assertEqual(create_post(1," test post 2."),1)

    def test_like_post(self):
        self.assertEqual(like_post(1,1),'1')
        self.assertEqual(like_post(1,1),'0')

    def test_update_post(self):
        self.assertEqual(update_post(1,""),'update failed')
        self.assertEqual(update_post(1,"    "),'update failed')
        self.assertEqual(update_post(1,"Update post."),1)

    def test_create_comment(self):
        self.assertEqual(create_comment(1,1,""),'comment failed')
        self.assertEqual(create_comment(1,1,"    "),'comment failed')
        self.assertEqual(create_comment(1,1,"test comment."),1)

    def test_like_comment(self):
        self.assertEqual(like_comment(1,1),'1')
        self.assertEqual(like_comment(1,1),'0')

    def test_update_comment(self):
        self.assertEqual(update_comment(1,""),'update failed')
        self.assertEqual(update_comment(1,"    "),'update failed')
        self.assertEqual(update_comment(1,"Update comment."),1)

    def test_change_password(self):
        self.assertEqual(change_password(1,"12345","12345"),'short')
        self.assertEqual(change_password(1,"111111","222222"),'wrongPWD')
        self.assertEqual(change_password(1,"1    1","1    1"),'notPWD')
        self.assertEqual(change_password(1,"123123","123123"),'samePWD')
        self.assertEqual(change_password(1,"qweqwe","qweqwe"),1)


if __name__ == '__main__':
    unittest.main(verbosity=2)