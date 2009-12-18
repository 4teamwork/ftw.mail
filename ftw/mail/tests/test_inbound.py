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
        
    def test_from(self):
        request = TestRequest(mail=self.ascii)
        mtool = getToolByName(self.portal, 'portal_membership')
        mtool.addMember('user1', 'u1', ['Member'], [],
                        {'email': 'from@example.org',
                         'fullname': 'User #1'})
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        view()
