
import main
import os
import unittest
import tempfile


class PasterTestCase(unittest.TestCase):

    def setUp(self):

        self.db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(main.app.config['DATABASE'])

    def test_paste_raw(self):
        rv = self.app.post('/', data=dict(lexer='python', paste='#test\r\npython = code\r\nprint("hello world")'),
                           follow_redirects=True)
        data = rv.data.decode("utf-8")
        assert """#test
python = code
print(&#34;hello world&#34;)""" not in data

    def test_delete_same_user(self):
        rv = self.app.post('/', data=dict(lexer='python', paste='#test\r\npython = code\r\nprint("hello world")'))
        loc = rv.location
        rv = self.app.get(loc)
        rv = self.app.get(loc)
        data = rv.data.decode("utf-8")
        assert """#test
python = code
print(&#34;hello world&#34;)""" not in data

    def test_delete_another_user(self):
        rv = self.app.post('/', data=dict(lexer='python', paste='#test\r\npython = code\r\nprint("hello world")',
                                        seen_delete=True
                                         ))
        loc = rv.location
        rv = self.app.get(loc)
        data = rv.data.decode("utf-8")
        assert """#test
python = code
print(&#34;hello world&#34;)""" not in data
        self.app.get(loc,  environ_base={'REMOTE_ADDR': "123.123.123.123"})
        rv = self.app.get(loc)
        data = rv.data.decode("utf-8")
        assert 'Paste Not Found =(\n' not in data

if __name__ == '__main__':
    unittest.main()