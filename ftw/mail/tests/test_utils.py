import unittest
import email
from email.MIMEText import MIMEText
from ftw.mail import utils


class TestUtils(unittest.TestCase):
    """Unit test for the Program type
    """
    
    def test_get_header(self):
        msg = MIMEText('foo')
        msg['To'] = 'nomail@no.net'
        self.assertEquals('nomail@no.net', utils.get_header(msg, 'To'))        
        msg.replace_header('To', '=?iso-8859-1?q?Hans M=FCller?= <nomail@no.net>')
        self.assertEquals('Hans M\xc3\xbcller <nomail@no.net>', utils.get_header(msg, 'To'))
        msg.replace_header('To', '=?utf-8?q?Hans M=C3=BCller?= <nomail@no.net>')
        self.assertEquals('Hans M\xc3\xbcller <nomail@no.net>', utils.get_header(msg, 'To'))

    def test_get_payload(self):
        # a plain text mail, iso-8859-1 charset, quoted-printable
        msg_str = 'Content-Type: text/plain; charset="iso-8859-1"\nMIME-Version: 1.0\n'\
                  'Content-Transfer-Encoding: quoted-printable\n\n'\
                  'Testing german umlauts: =E4=F6=FC=C4=D6=DC'
        msg = email.message_from_string(msg_str)
        self.assertEquals('Testing german umlauts: \xc3\xa4\xc3\xb6\xc3\xbc\xc3\x84\xc3\x96\xc3\x9c',
                           utils.get_payload(msg))
        # a plain text mail, utf8 charset, base64
        msg_str = 'Content-Type: text/plain; charset="utf8"\nMIME-Version: 1.0\n'\
                  'Content-Transfer-Encoding: base64\n\n'\
                  'VGVzdGluZyBnZXJtYW4gdW1sYXV0czogw6TDtsO8w4TDlsOc\n'
        msg = email.message_from_string(msg_str)
        self.assertEquals('Testing german umlauts: \xc3\xa4\xc3\xb6\xc3\xbc\xc3\x84\xc3\x96\xc3\x9c',
                           utils.get_payload(msg))

    def test_get_best_alternative(self):
        # prefer html over plain text
        alternatives = ['text/html', 'text/plain']
        self.assertEquals(0, utils.get_best_alternative(alternatives))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)