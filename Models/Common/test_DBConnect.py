from unittest import TestCase
from DBUtils import DBConnect


class TestDBConnect(TestCase):

    def test_query(self):
        try:
            db = DBConnect()
            df = db.query("SELECT * FROM open_close LIMIT 1")
            if df.empty:
                raise Exception
        except:
            self.fail()
