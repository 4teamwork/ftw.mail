from Products.PloneTestCase.ptc import PloneTestCase
from zExceptions import NotFound
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter
from ftw.mail.tests.layer import Layer
from ftw.mail.mail import IMail


class TestInboundMail(PloneTestCase):

    layer = Layer

    def test_no_message(self):
        view = self.portal.restrictedTraverse('@@mail-inbound')
        self.assertRaises(IOError, view)

    def test_invalid_message(self):
        request = TestRequest(mail=1)
        view = getMultiAdapter((self.portal, request), name='mail-inbound')
        self.assertRaises(IOError, view)

        