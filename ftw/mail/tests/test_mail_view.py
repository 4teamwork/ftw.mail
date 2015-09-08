from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
import os.path


def mail_asset(name, ext='txt'):
    tests_dir_path = os.path.dirname(__file__)
    filename = '.'.join((name, ext))
    return open(os.path.join(tests_dir_path, 'mails', filename))


class TestMailView(TestCase):
    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    @browsing
    def test_heading_is_subject(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'Die B\xfcrgschaft', plone.first_heading())

    @browsing
    def test_From_header(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'from@example.org',
                          browser.css('.mailFrom td').first.text)

    @browsing
    def test_Subject_header(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'Die B\xfcrgschaft',
                          browser.css('.mailSubject td').first.text)

    @browsing
    def test_Date_header(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'Jan 01, 1970 01:00 AM',
                          browser.css('.mailDate td').first.text)

    @browsing
    def test_To_header(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'Friedrich H\xf6lderlin <to@example.org>',
                          browser.css('.mailTo td').first.text)

    @browsing
    def test_CC_header(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('latin1')))
        browser.login().visit(mail)
        self.assertEquals(u'cc@example.org',
                          browser.css('.mailCc td').first.text)

    @browsing
    def test_body(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('utf8')))
        browser.login().visit(mail)
        body_lines = browser.css('.mailBody').first.text.split('\n')
        self.assertIn(u'Friedrich Schiller', body_lines)
        self.assertIn(u'\xbbDie Stadt vom Tyrannen befreien!\xab', body_lines)

    @browsing
    def test_attachments(self, browser):
        mail = create(Builder('mail')
                      .with_message(mail_asset('nested_attachments')))
        browser.login().visit(mail)

        # Plone <= 4.1 uses "kB",
        # Plone >= 4.2 uses "KB"
        # Therefore we just lowercase it in the test because it is not relevant.

        self.assertItemsEqual(
            ['1703693_0412c29a4f.jpg file 134.4 kb',
             '3512536451_e1310bf568.jpg file 218.3 kb'],
            map(str.lower, browser.css('.mailAttachment').text))

    @browsing
    def test_mail_body_is_html_safe(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('xxs_mail')))
        browser.login().visit(mail)

        self.assertNotIn("alert('hello')", browser.contents,
                         "Javascript gets not removed by the mail view.")

    @browsing
    def test_mail_body_contains_all_html_parts(self, browser):
        """Regression:
        """
        mail = create(Builder('mail').with_message(mail_asset('multiple_html_parts')))
        browser.login().visit(mail)
        self.assertEquals('Hello World',
                          browser.css('.mailBody').first.text)

    @browsing
    def test_style_blocks_get_parsed(self, browser):
        mail = create(Builder('mail').with_message(mail_asset('xxs_mail')))
        browser.login().visit(mail)

        self.assertEquals(
            'color:red; size:18px',
            browser.css('.mailBody h1').first.get('style'))

        self.assertNotIn(
            '<style>', browser.contents,
            '<style> tags gets not wrapped correctly with the wrapper class.')

    @browsing
    def test_fixes_broken_meta_tags(self, browser):
        mail = create(Builder('mail')
                      .with_message(mail_asset('broken_meta_tags')))
        browser.login().visit(mail)

        # This part is latin1 encoded, as declared by the MIME part's
        # Content-Type as well as a broken <meta /> tag with a charset
        latin1_encoded_part = browser.css('.mailBody-part')[2]

        self.assertIn(
            u'B\xe4rengraben', latin1_encoded_part.text,
            'The latin1 encoded text/html part should be properly re-encoded')

        meta = latin1_encoded_part.xpath('meta').first
        self.assertEquals(
            'text/html; charset=utf-8', meta.attrib['content'],
            '<meta /> tag should have been rewritten by zope.pagetemplate')
