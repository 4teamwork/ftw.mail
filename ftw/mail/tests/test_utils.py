# -*- coding: utf-8 -*-
from copy import deepcopy
from email.MIMEText import MIMEText
from ftw.mail import utils
import email
import os
import unittest2


class TestUtils(unittest2.TestCase):
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
        msg_txt = open(os.path.join(here, 'mails', 'attachment.txt'), 'r').read()
        self.msg_attachment = email.message_from_string(msg_txt)
        msg_txt = open(os.path.join(here, 'mails', 'fwd_attachment.txt'), 'r').read()
        self.msg_fwd_attachment = email.message_from_string(msg_txt)
        msg_txt = open(os.path.join(here, 'mails', 'nested_attachments.txt'), 'r').read()
        self.msg_nested_attachments = email.message_from_string(msg_txt)
        msg_txt = open(os.path.join(here, 'mails', 'nested_referenced_image_attachment.txt'),
                       'r').read()
        self.nested_referenced_image_attachment = email.message_from_string(msg_txt)

    def test_get_header(self):
        self.assertEquals('', utils.get_header(self.msg_empty, 'Subject'))
        self.assertEquals('Lorem Ipsum',
                          utils.get_header(self.msg_ascii, 'Subject'))
        self.assertEquals('Die B\xc3\xbcrgschaft',
                          utils.get_header(self.msg_latin1, 'Subject'))
        self.assertEquals('Friedrich H\xc3\xb6lderlin <to@example.org>',
                          utils.get_header(self.msg_latin1, 'To'))
        self.assertEquals('Die B\xc3\xbcrgschaft',
                          utils.get_header(self.msg_utf8, 'Subject'))
        self.assertEquals('Friedrich H\xc3\xb6lderlin <to@example.org>',
                          utils.get_header(self.msg_utf8, 'To'))

    def test_get_date_header(self):
        # a date header
        msg_txt = 'Date: Thu, 01 Jan 1970 01:00:00 +0100'
        msg = email.message_from_string(msg_txt)
        self.assertEquals(0.0, utils.get_date_header(msg, 'Date'))
        # a date header with timezone name
        msg_txt = 'Date: Sat, 14 Feb 2009 00:31:30 +0100 (CET)'
        msg = email.message_from_string(msg_txt)
        self.assertEquals(1234567890.0, utils.get_date_header(msg, 'Date'))
        # an unparsable date header
        msg_txt = 'Date: at any time ...'
        msg = email.message_from_string(msg_txt)
        self.assertEqual(0.0, utils.get_date_header(msg, 'Date'))

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

    def test_get_filename(self):
        msg_txt = \
            """Content-Type: application/octet-stream;
  name="=?iso-8859-1?Q?Aperovorschl=E4ge_2010=2Epdf?="
Content-Transfer-Encoding: base64
Content-Description: =?iso-8859-1?Q?Aperovorschl=E4ge_2010=2Epdf?=
Content-Disposition: attachment;
  filename="=?iso-8859-1?Q?Aperovorschl=E4ge_2010=2Epdf?="
"""
        msg = email.message_from_string(msg_txt)
        # !!! seems to be a bug in email package
        self.assertEquals('Aperovorschläge 2010.pdf', utils.get_filename(msg))

        msg_txt = \
        """Content-Disposition: attachment;
	filename*=iso-8859-1''f%F6rmularz%FCgriffsber%E4chtigungen.doc
Content-Type: application/msword;
	name*=iso-8859-1''f%F6rmularz%FCgriffsber%E4chtigungen.doc
Content-Transfer-Encoding: base64
"""
        msg = email.message_from_string(msg_txt)
        self.assertEquals('f\xc3\xb6rmularz\xc3\xbcgriffsber\xc3\xa4chtigungen.doc', utils.get_filename(msg))

    def test_get_attachments(self):
        self.assertEquals([], utils.get_attachments(self.msg_ascii))
        self.assertEquals([{'position': 1,
                            'size': 7,
                            'content-type': 'text/plain',
                            'filename': 'Bücher.txt'}],
                          utils.get_attachments(self.msg_attachment))

    def test_nested_get_attachments(self):
        """A forwarded mail with attachments results in nested multipart
        payloads - this should also be handled by get_attachments method.
        """
        self.assertEquals([{'position': 4,
                            'size': 137588,
                            'content-type': 'image/jpg',
                            'filename': '1703693_0412c29a4f.jpg'},
                           {'position': 5,
                            'size': 223504,
                            'content-type': 'image/jpg',
                            'filename': '3512536451_e1310bf568.jpg'}],
                          utils.get_attachments(self.msg_nested_attachments))

    def test_remove_attachments(self):
        # we dont want to change the message itselve, so lets copy it
        msg = deepcopy(self.msg_attachment)
        self.assertNotEquals(msg, self.msg_attachment)

        # our message has one attachment
        self.assertEquals([{'position': 1,
                            'size': 7,
                            'content-type': 'text/plain',
                            'filename': 'Bücher.txt'}],
                          utils.get_attachments(msg))

        # lets remove the attachment
        new_msg = utils.remove_attachments(msg, (1,))

        # we get the same message back
        self.assertEquals(msg, new_msg)
        self.assertEquals([], utils.get_attachments(new_msg))

    def test_nested_remove_attachments(self):
        """A forwarded mail with attachments results in nested multipart
        payloads - this should also be handled by remove_attachments.
        """
        msg = deepcopy(self.msg_nested_attachments)
        self.assertNotEquals(msg, self.msg_nested_attachments)

        # we have two attachments (which are nested)
        self.assertEquals([{'position': 4,
                            'size': 137588,
                            'content-type': 'image/jpg',
                            'filename': '1703693_0412c29a4f.jpg'},
                           {'position': 5,
                            'size': 223504,
                            'content-type': 'image/jpg',
                            'filename': '3512536451_e1310bf568.jpg'}],
                          utils.get_attachments(msg))

        # lets remove one attachment
        new_msg = utils.remove_attachments(msg, (5,))

        # we get the same message back..
        self.assertEquals(msg, new_msg)
        # .. but without the removed attachment
        self.assertEquals([{'position': 4,
                            'size': 137588,
                            'content-type': 'image/jpg',
                            'filename': '1703693_0412c29a4f.jpg'}],
                          utils.get_attachments(new_msg))

    def test_unwrap_html_body(self):
        html = """
        <html>
        <head></head>
        <body>Body</body>
        </html>
        """
        body = '<div>Body</div>'
        self.assertEquals(body, utils.unwrap_html_body(html))
        html = """
        <html>
        <body style="color: #666; font-size: 12px;">Body</body>
        </html>
        """
        body ='<div class="mailBody" style="color: #666; font-size: 12px;">'\
            'Body</div>'
        self.assertEquals(body, utils.unwrap_html_body(html, 'mailBody'))
        html = '<p>Body</p>'
        body = '<div class="mailBody"><p>Body</p></div>'
        self.assertEquals(body, utils.unwrap_html_body(html, 'mailBody'))

    def test_unwrap_html_body_encoding(self):
        # the html body may contain a charset header
        # we always get an utf8-encoded body, thus we must ignore the charset
        html = """
        <html>
        <head>
        <meta http-equiv=Content-Type content="text/html; charset=iso-8859-1">
        </head>
        <body>Äöü</body>
        """
        self.assertEquals('<div>Äöü</div>', utils.unwrap_html_body(html))

        # BeautifulSoup does some weird encoding guessing.
        # For the snippet above it guesses utf-8, but if the body
        # only contains a single ä Umlaut, it seems to guess latin1.
        # Check we still get utf-8 back.
        html = """
        <html>
        <body>ä</body>
        """
        self.assertEquals('<div>ä</div>', utils.unwrap_html_body(html))

    def test_unwrap_attached_msg(self):
        msg = utils.unwrap_attached_msg(self.msg_fwd_attachment)
        self.assertEquals(msg.get('Subject'), 'Lorem Ipsum')

    def test_get_position_for_cid(self):
        self.assertEqual(4, utils.get_position_for_cid(
            self.nested_referenced_image_attachment,
            'BB5DB00F-5C9A-4866-894D-8468D4B320F8'))

    def test_adjust_image_tags_generates_correct_links(self):
        html = ''.join(
            utils.get_text_payloads(self.nested_referenced_image_attachment))

        self.assertNotIn('get_attachment?position=4', html)
        html = utils.adjust_image_tags(html,
                                       self.nested_referenced_image_attachment,
                                       'foo')
        self.assertIn('get_attachment?position=4', html)


def test_suite():
    return unittest2.defaultTestLoader.loadTestsFromName(__name__)
