
import unittest
from server import *

class TestServer(unittest.TestCase):

    def test_space(self):
        st1 = "                   "
        st2 = "   Email           "
        st3 = "   John    Titor   "
        self.assertEqual(format_space(st1),0)
        self.assertEqual(format_space(st2),"Email")
        self.assertEqual(format_space(st3),"John Titor")

    def test_email(self):
        email1 = "123@bjtu.edu.cn"
        email2 = "gmail@.com"
        email3 = "John Titor"
        self.assertEqual(validate_email(email1),1)
        self.assertEqual(validate_email(email2),0)
        self.assertEqual(validate_email(email3),0)

    def test_create_user(self):
        
        CONN = psycopg2.connect(dbname="testDB", user="postgres",
            password="456",host="127.0.0.1", port="5432")
        self.assertEqual(create_user("123@qwe.com","Foo Bar","123123","0"),0)
        self.assertEqual(create_user("123@qwe.com","XXX","999999","0"),"users_email_key")
        self.assertEqual(create_user("456@qwe.com","Foo Bar","123123","0"),"users_name_key")

if __name__ == '__main__':
    unittest.main()
