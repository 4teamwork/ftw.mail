# -*- coding: utf-8 -*-
from copy import deepcopy
from email.MIMEText import MIMEText
from ftw.mail import utils
from ftw.mail.tests import mails
import email
import unittest2


def pop_size(attachments):
    """Pop fs/os dependent size from attachment metadata dict.
    """
    for each in attachments:
        each.pop('size', None)
    return attachments


class TestUtils(unittest2.TestCase):

    maxDiff = None

    def setUp(self):
        # setup some test mails
        self.msg_empty = MIMEText('')
        self.msg_ascii = mails.load_mail(
            'ascii_7bit.txt')
        self.msg_latin1 = mails.load_mail(
            'latin1.txt')
        self.msg_utf8 = mails.load_mail(
            'utf8.txt')
        self.msg_attachment = mails.load_mail(
            'attachment.txt')
        self.msg_fwd_attachment = mails.load_mail(
            'fwd_attachment.txt')
        self.msg_nested_attachments = mails.load_mail(
            'nested_attachments.txt')
        self.nested_referenced_image_attachment = mails.load_mail(
            'nested_referenced_image_attachment.txt')
        self.msg_multiple_html_parts = mails.load_mail(
            'multiple_html_parts.txt')
        self.multipart_encoded_with_attachments = mails.load_mail(
            'multipart_encoded_with_attachments.txt')
        self.from_header_with_quotes = mails.load_mail(
            'from_header_with_quotes.txt')
        self.encoded_word_without_lwsp = mails.load_mail(
            'encoded_word_without_lwsp.txt')
        self.newline_in_header = mails.load_mail(
            'newline_in_header.txt')
        self.sticky_encoded_words_in_subject = mails.load_mail(
            'encoded_word_not_separated_by_lwsp.txt')

    def test_walk_signed(self):
        msg = mails.load_mail('signed.eml')
        parts = list(utils.walk(msg))

        self.assertEqual(7, len(parts))
        self.assertEqual(
            ['multipart/mixed', 'text/plain', 'multipart/signed',
             'multipart/signed', 'multipart/mixed', 'text/plain',
             'application/x-pkcs7-signature'],
            [each.get_content_type() for each in parts])

    def test_get_attachments_signed(self):
        msg = mails.load_mail('signed.eml')
        self.assertEquals(
            [{'position': 2,
            'content-type': 'multipart/signed',
            'filename': 'smime.p7m'},
            {'position': 6,
             'content-type':
             'application/x-pkcs7-signature',
             'filename': 'smime.p7s'}],
            pop_size(utils.get_attachments(msg)))

    def test_get_attachments_signed_with_attachments(self):
        msg = mails.load_mail('signed_with_attachments.eml')
        self.assertEquals(
           [{'position': 4,
            'content-type': 'multipart/signed',
            'filename': 'smime.p7m'},
           {'position': 8,
            'content-type': 'application/pdf',
            'filename': 'Testdatei.pdf'},
           {'position': 9,
            'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'filename': 'Testdatei.docx'},
           {'position': 10,
            'content-type': 'application/pkcs7-signature',
            'filename': 'smime.p7s'}],
           pop_size(utils.get_attachments(msg)))

    def test_walk_signed_with_attachments(self):
        msg = mails.load_mail('signed_with_attachments.eml')
        parts = list(utils.walk(msg))

        self.assertEqual(11, len(parts))
        self.assertEqual(
            ['multipart/mixed', 'multipart/alternative', 'text/plain',
             'application/rtf', 'multipart/signed', 'multipart/signed',
             'multipart/mixed', 'text/plain', 'application/pdf',
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             'application/pkcs7-signature'],
            [each.get_content_type() for each in parts])

    def test_get_attachments_signed_nested_with_attachments(self):
        msg = mails.load_mail('signed_nested_with_attachments.eml')
        self.assertEquals(
            [{'position': 4,
              'content-type': 'multipart/signed',
              'filename': 'smime.p7m'},
             {'position': 12,
              'content-type': 'application/pdf',
              'filename': 'Testdatei.pdf'},
             {'position': 13,
              'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
              'filename': 'Testdatei.docx'},
             {'position': 14,
              'content-type': 'application/pkcs7-signature',
              'filename': 'smime.p7s'},
             {'position': 15,
              'content-type': 'application/pkcs7-signature',
              'filename': 'smime.p7s'}],
            pop_size(utils.get_attachments(msg)))

    def test_walk_signed_nested_with_attachments(self):
        msg = mails.load_mail('signed_nested_with_attachments.eml')
        parts = list(utils.walk(msg))

        self.assertEqual(16, len(parts))
        self.assertEqual(
            ['multipart/mixed', 'multipart/alternative', 'text/plain',
             'application/rtf', 'multipart/signed', 'multipart/signed',
             'multipart/mixed', 'text/plain', 'message/rfc822',
             'multipart/signed', 'multipart/mixed', 'text/plain',
             'application/pdf',
             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             'application/pkcs7-signature', 'application/pkcs7-signature'],
            [each.get_content_type() for each in parts])

    def test_walk_util_and_walk_yield_same_for_non_signed_multipart(self):
        self.assertEqual(
            list(self.msg_empty.walk()),
            list(utils.walk(self.msg_empty)))
        self.assertEqual(
            list(self.msg_ascii.walk()),
            list(utils.walk(self.msg_ascii)))
        self.assertEqual(
            list(self.msg_latin1.walk()),
            list(utils.walk(self.msg_latin1)))
        self.assertEqual(
            list(self.msg_utf8.walk()),
            list(utils.walk(self.msg_utf8)))
        self.assertEqual(
            list(self.msg_attachment.walk()),
            list(utils.walk(self.msg_attachment)))
        self.assertEqual(
            list(self.msg_fwd_attachment.walk()),
            list(utils.walk(self.msg_fwd_attachment)))
        self.assertEqual(
            list(self.msg_nested_attachments.walk()),
            list(utils.walk(self.msg_nested_attachments)))
        self.assertEqual(
            list(self.nested_referenced_image_attachment.walk()),
            list(utils.walk(self.nested_referenced_image_attachment)))
        self.assertEqual(
            list(self.msg_multiple_html_parts.walk()),
            list(utils.walk(self.msg_multiple_html_parts)))
        self.assertEqual(
            list(self.multipart_encoded_with_attachments.walk()),
            list(utils.walk(self.multipart_encoded_with_attachments)))
        self.assertEqual(
            list(self.from_header_with_quotes.walk()),
            list(utils.walk(self.from_header_with_quotes)))
        self.assertEqual(
            list(self.encoded_word_without_lwsp.walk()),
            list(utils.walk(self.encoded_word_without_lwsp)))
        self.assertEqual(
            list(self.newline_in_header.walk()),
            list(utils.walk(self.newline_in_header)))
        self.assertEqual(
            list(self.sticky_encoded_words_in_subject.walk()),
            list(utils.walk(self.sticky_encoded_words_in_subject)))

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

    def test_get_from_header_with_quotes(self):
        self.assertEquals(
            '"Mueller-Valser, Gabriela" <gabriela.mueller@example.org>',
            self.from_header_with_quotes['From'])

        self.assertEquals(
            '"Mueller-Valser, Gabriela" <gabriela.mueller@example.org>',
            utils.get_header(self.from_header_with_quotes, 'From'))

    def test_get_header_fixes_encoded_words_without_lwsp(self):
        self.assertEquals(
            'B\xc3\xa4rengraben <to@example.org>',
            utils.get_header(self.encoded_word_without_lwsp, 'To'))

        # Should not insert additional whitespace between encoded words
        self.assertEquals(
            'B\xc3\xa4rengrabenB\xc3\xa4rengraben <from@example.org>',
            utils.get_header(self.encoded_word_without_lwsp, 'From'))

    def test_get_header_fixes_encoded_words_with_newlines(self):
        self.assertEquals(
            'Email: QP B\xc3\xbcschelisheimat   / Aktennotiz vom 27.02.2017',
            utils.get_header(self.newline_in_header, 'Subject')
        )

    def test_safe_decode_header_fixes_encoded_words_without_lwsp_in_middle(self):
        header = 'Foo =?utf-8?Q?B=C3=A4rengraben?=\r\n <from@example.org>'
        self.assertEquals(
            'Foo B\xc3\xa4rengraben <from@example.org>',
            utils.safe_decode_header(header))

    def test_get_subject_header_with_sticky_encoded_words(self):
        self.assertEquals(
            'Bärengraben',
            utils.get_header(self.sticky_encoded_words_in_subject, 'Subject'))

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
        self.assertEqual(None, utils.get_date_header(msg, 'Date'))

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
        self.assertEquals(0, len(utils.get_body(self.msg_empty)))
        self.assertEquals('<p>Lorem ipsum', utils.get_body(self.msg_ascii)[0][:14])

    def test_get_body_returns_each_html_document_separately(self):
        parts = utils.get_body(self.msg_multiple_html_parts)
        self.assertEquals(2, len(parts), 'Expected two html parts.')
        self.assertIn('Hello', parts[0])
        self.assertIn('World', parts[1])

    def test_can_decode_encoded_multipart_attachments(self):
        expected_attachments = [{
            'content-type': 'message/delivery-status',
            'filename': 'ATT74209.txt',
            'position': 4,
            'size': 0,
            }]
        attachments = utils.get_attachments(self.multipart_encoded_with_attachments)
        self.assertEqual(expected_attachments, attachments)

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
        body = '<div class="mailBody" style="color: #666; font-size: 12px;">Body</div>'
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
