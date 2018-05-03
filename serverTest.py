import unittest
from serverCopy import *

class TestServer(unittest.TestCase):

    @classmethod
    def tearDownClass(self):
        cur = CONN.cursor()
        cur.execute("DELETE FROM users;")
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
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123123","123123","0"),None)
        self.assertEqual(create_user("invalidEmail","Foo Bar","123123","123123","0"),"invalidEmail")
        self.assertEqual(create_user("123@qwe.com","         ","123123","123123","0"),"noName")
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123","123","0"),"short")
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123123","999999","0"),"wrongPWD")
        self.assertEqual(create_user("123@qwe.com","XXX","999999","999999","0"),"users_email_key")
        self.assertEqual(create_user("456@qwe.com","Foo Bar","123123","123123","0"),"users_name_key")

    def test_user_login(self):
        self.assertIsInstance(user_login("123@qwe.com","123123"),int)
        self.assertIsInstance(user_login("    Foo    Bar   ","123123"),int)
        self.assertEqual(user_login("No Name","123123"),"noName")
        self.assertEqual(user_login("123@qwe.com","999999"),"wrongPWD")

if __name__ == '__main__':
    unittest.main(verbosity=2)