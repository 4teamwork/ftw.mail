# -*- coding: utf-8 -*-
import os
from email.MIMEText import MIMEText
from Products.PloneTestCase.ptc import PloneTestCase
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from ftw.mail.tests.layer import Layer
from ftw.mail.mail import IMail
from ftw.mail.interfaces import IMailInbound, IDestinationResolver


class TestInboundMail(PloneTestCase):

    layer = Layer

    def afterSetUp(self):
        here = os.path.dirname(__file__)
        self.ascii = open(os.path.join(here, 'mails', 'ascii_7bit.txt'), 'r').read()
        self.resent = open(os.path.join(here, 'mails', 'resent.txt'), 'r').read()
        # setup recipient and sender email addresses for test user
        mtool = getToolByName(self.portal, 'portal_membership')
        user = mtool.getAuthenticatedMember()
        user.setMemberProperties(dict(email='from@example.org'))
        id_util = getUtility(IIntIds)

        # Make intids work in tests
        id_util.register(self.folder)

        intid = id_util.queryId(self.folder)
        self.mail_to = '%s@example.org' % intid

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


    def test_intid_resolver(self):
        self.folder.invokeFactory('Folder', 'f1')
        f1 = self.folder['f1']
        id_util = getUtility(IIntIds)
        intid = id_util.queryId(f1)
        class DummyMailInbound:
            implements(IMailInbound)
            def __init__(self, context):
                self.context = context
            def msg(self):
                return MIMEText('')
            def sender(self):
                return ''
            def recipient(self):
                return '%s@example.org' % intid
        resolver = IDestinationResolver(DummyMailInbound(self.portal))
        self.assertEquals(f1, resolver.destination())

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
                  'Subject: Here comes a tab	and some umlauts äöü' % self.mail_to
        request = TestRequest(mail=msg_txt)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertEquals('0:OK', view())
