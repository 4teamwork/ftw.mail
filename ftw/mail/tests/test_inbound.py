# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
import os


class TestInboundMail(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestInboundMail, self).setUp()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

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
                  'Subject: Here comes a tab	and some umlauts \xc3\xa4\xc3\xb6\xc3\xbc' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())
