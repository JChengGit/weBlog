
import unittest
from serverFunc import *

class TestServer(unittest.TestCase):

    def test_space(self):
        st1 = "                   "
        st2 = "   Email           "
        st3 = "   John    Titor   "
        self.assertEquals(format_space(st1),0)
        self.assertEquals(format_space(st2),"Email")
        self.assertEquals(format_space(st3),"John Titor")

    def test_email(self):
        email1 = "123@bjtu.edu.cn"
        email2 = "gmail@.com"
        email3 = "John Titor"
        self.assertEquals(validate_email(email1),1)
        self.assertEquals(validate_email(email2),0)
        self.assertEquals(validate_email(email3),0)

if __name__ == '__main__':
    unittest.main()
