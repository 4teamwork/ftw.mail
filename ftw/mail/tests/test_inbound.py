# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IMailSettings
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import TestRequest
import os


def asset(filename):
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'mails', filename)
    with open(path, 'r') as file_:
        return file_.read()


class TestInboundMail(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestInboundMail, self).setUp()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.setChainForPortalTypes(('Folder',),
                                      ('simple_publication_workflow',))

        self.folder = create(Builder('folder'))

        here = os.path.dirname(__file__)
        self.ascii = open(os.path.join(here, 'mails', 'ascii_7bit.txt'), 'r').read()
        self.resent = open(os.path.join(here, 'mails', 'resent.txt'), 'r').read()
        # setup recipient and sender email addresses for test user
        mtool = getToolByName(self.portal, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        user.setMemberProperties(dict(email='from@example.org'))

        emailaddress = IEmailAddress(TestRequest())
        self.mail_to = emailaddress.get_email_for_object(self.folder)

        logout()

    def test_no_message(self):
        view = self.portal.restrictedTraverse('@@mail-inbound')
        self.assertEquals('66:No mail message supplied.', view())

    def test_invalid_message(self):
        request = TestRequest(mail=1)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('65:Invalid mail message supplied.', view())

    def test_sender(self):
        request = TestRequest(mail=self.ascii)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('from@example.org', view.sender())
        request = TestRequest(mail=self.resent)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('resent.from@example.org', view.sender())

    def test_recipient(self):
        request = TestRequest(mail=self.ascii)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('to@example.org', view.recipient())
        request = TestRequest(mail=self.resent)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('resent.to@example.org', view.recipient())

    def test_recipient_from_request(self):
        request = TestRequest(mail=self.ascii)
        request.form['recipient'] = 'recipient@example.org'
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('recipient@example.org', view.recipient())
        request = TestRequest(mail=self.resent)
        request.form['recipient'] = 'recipient@example.org'
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('recipient@example.org', view.recipient())

    def test_unknown_sender(self):
        # unknown sender
        msg_txt = 'To: to@example.org\n'\
            'From: unknown@example.org\n'\
            'Subject: Test'
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('77:Unknown sender. Permission denied.', view())
        # known upper-case sender, lower-case member email
        msg_txt = 'To: %s\n'\
            'From: FROM@example.org\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

        # known lower-case sender, upper-case member email
        login(self.portal, TEST_USER_NAME)
        mtool = getToolByName(self.portal, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        user.setMemberProperties(dict(email='FROM@example.org'))
        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

    def test_unknown_destination(self):
        msg_txt = 'To: unknown@example.org\n'\
            'From: from@example.org\n'\
            'Subject: Test'
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('73:Destination does not exist.', view())

    def test_mail_creation(self):
        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

    def test_long_header(self):
        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: A long mail header with more than 78 characters.'\
            'Lorem ipsum dolor sit amet, consectetur adipisicing elit,'\
            ' sed do eiusmod tempor incididunt ut labore et dolore '\
            'magna aliqua.' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

    def test_weird_characters_in_subject(self):
        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: Here comes a tab  and some umlauts \xc3\xa4\xc3\xb6\xc3\xbc' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

    def test_inbound_view_returns_text_plain(self):
        msg_txt = 'To: %s\n'\
            'From: FROM@example.org\n'\
            'Subject: Test' % self.mail_to
        self.portal.REQUEST.set("mail", msg_txt)
        view = self.portal.restrictedTraverse("mail-inbound")
        view()
        self.assertEquals(
            "text/plain",
            self.portal.REQUEST.response.getHeader('Content-Type'))

    def test_no_sender_email(self):
        msg_txt = 'To: %s\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('77:Could not extract sender email.', view())

    def test_nested_mail_is_unwrapped(self):
        create(Builder('user').with_email('fwd.from@example.org')
               .with_roles('Contributor', on=self.folder))
        mail = asset('fwd_attachment.txt')
        mail = mail.replace('To: fwd.to@example.org', 'To: %s' % self.mail_to)

        request = TestRequest(mail=mail)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

        obj = self.folder.get('lorem-ipsum')
        self.assertEquals('Lorem Ipsum', obj.Title())

    def test_nested_mail_no_unwrapping(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSettings)
        settings.unwrap_mail = False

        create(Builder('user').with_email('fwd.from@example.org')
               .with_roles('Contributor', on=self.folder))
        mail = asset('fwd_attachment.txt')
        mail = mail.replace('To: fwd.to@example.org', 'To: %s' % self.mail_to)

        request = TestRequest(mail=mail)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())

        obj = self.folder.get('fwd-lorem-ipsum')
        self.assertEquals('Fwd: Lorem Ipsum', obj.Title())

    def test_unauthorized_to_add_mails(self):
        self.folder.manage_permission('ftw.mail: Add Inbound Mail',
                                      roles=[], acquire=False)

        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')

        self.assertEquals('77:Unable to create message. Permission denied.',
                          view())

    def test_mails_not_addable(self):
        ttool = getToolByName(self.portal, 'portal_types')
        ttool.get('ftw.mail.mail').global_allow = False

        msg_txt = 'To: %s\n'\
            'From: from@example.org\n'\
            'Subject: Test' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')

        self.assertEquals('77:Disallowed subobject type. Permission denied.',
                          view())
