from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from ftw.mail.tests.test_mail_view import mail_asset
from ftw.testbrowser import browsing
from StringIO import StringIO
from unittest2 import TestCase
from zipfile import ZipFile


class TestMailView(TestCase):
    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        self.mail = create(Builder('mail').with_message(mail_asset('latin1')))

    @browsing
    def test_zipexport_works_on_mail(self, browser):
        browser.login().visit(self.mail, view='zip_export')
        self.assertEquals('application/zip', browser.headers['Content-Type'])
        self.assertEquals("attachment; filename*=utf-8''Die%20B%C3%BCrgschaft.zip",
                          browser.headers['Content-Disposition'])

        zipfile = ZipFile(StringIO(browser.contents))
        self.assertEquals(['message.eml'], zipfile.namelist())
        self.assertMultiLineEqual(mail_asset('latin1').read(),
                                  zipfile.read('message.eml'))
