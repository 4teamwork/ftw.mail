import unittest
import email
import os
from email.MIMEText import MIMEText
from ftw.mail import utils


class TestUtils(unittest.TestCase):
    """Unit test for the Program type
    """
    def setUp(self):
        # setup some test mails
        self.msg_empty = MIMEText('')
        here = os.path.dirname(__file__)
        msg_txt = open(os.path.join(here, 'mails', 'ascii_7bit.txt'), 'r').read()
        self.msg_ascii = email.message_from_string(msg_txt)
        msg_txt = open(os.path.join(here, 'mails', 'latin1.txt'), 'r').read()
        self.msg_latin1 = email.message_from_string(msg_txt)
        msg_txt = open(os.path.join(here, 'mails', 'utf8.txt'), 'r').read()
        self.msg_utf8 = email.message_from_string(msg_txt)
        
    def test_get_header(self):
        self.assertEquals('', utils.get_header(self.msg_empty, 'Subject'))
        self.assertEquals('Lorem Ipsum', utils.get_header(self.msg_ascii, 'Subject'))
        self.assertEquals('Die B\xc3\xbcrgschaft', utils.get_header(self.msg_latin1, 'Subject'))
        self.assertEquals('Friedrich H\xc3\xb6lderlin <to@example.org>', utils.get_header(self.msg_latin1, 'To'))
        self.assertEquals('Die B\xc3\xbcrgschaft', utils.get_header(self.msg_utf8, 'Subject'))
        self.assertEquals('Friedrich H\xc3\xb6lderlin <to@example.org>', utils.get_header(self.msg_utf8, 'To'))

    def test_get_payload(self):
        self.assertEquals('', utils.get_payload(self.msg_empty))
        self.assertEquals('Lorem ipsum', utils.get_payload(self.msg_ascii)[:11])
        self.assertEquals('Die B\xc3\xbcrgschaft', utils.get_payload(self.msg_latin1)[:15])
        self.assertEquals('Die B\xc3\xbcrgschaft', utils.get_payload(self.msg_utf8)[:15])

    def test_get_best_alternative(self):
        # prefer html over plain text
        alternatives = ['text/html', 'text/plain']
        self.assertEquals(0, utils.get_best_alternative(alternatives))

    def test_get_text_payloads(self):
        self.assertEquals([], utils.get_text_payloads(None))
        self.assertEquals(1, len(utils.get_text_payloads(self.msg_ascii)))

    def test_get_body(self):
        self.assertEquals('', utils.get_body(self.msg_empty))
        self.assertEquals('<p>Lorem ipsum', utils.get_body(self.msg_ascii)[:14])
        
    def test_get_attachments(self):
        self.assertEquals([], utils.get_attachments(self.msg_ascii))
        

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)