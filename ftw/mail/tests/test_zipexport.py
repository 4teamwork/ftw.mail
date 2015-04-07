from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from ftw.mail.tests.test_mail_view import mail_asset
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestMailView(TestCase):
    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        self.mail = create(Builder('mail').with_message(mail_asset('latin1')))

    @browsing
    def test_zipexport_works_on_mail(self, browser):

        browser.login().visit(self.mail, view='zip_export')
        self.assertIn('message.eml', browser.contents)
