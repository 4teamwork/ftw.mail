from email.MIMEText import MIMEText
from ftw.mail.interfaces import IMailInbound, IDestinationResolver
from ftw.mail.tests.layer import Layer
from plone.uuid.interfaces import IUUID
from Products.PloneTestCase.ptc import PloneTestCase
from zope.interface import implements


class TestUUIDResolver(PloneTestCase):

    layer = Layer

    def set_up_dummy_inbound(self):
        self.folder.invokeFactory('Folder', 'f1')
        f1 = self.folder['f1']
        uuid = IUUID(f1)

        class DummyMailInbound:
            implements(IMailInbound)
            def __init__(self, context):
                self.context = context
            def msg(self):
                return MIMEText('')
            def sender(self):
                return ''
            def recipient(self):
                return '%s@example.org' % uuid

        return f1, DummyMailInbound(self.portal)

    def test_uuid_resolver_destination(self):
        context, inbound = self.set_up_dummy_inbound()

        resolver = IDestinationResolver(inbound)
        self.assertEquals(context, resolver.destination())

    def test_uuid_resolver_uuid(self):
        context, inbound = self.set_up_dummy_inbound()

        resolver = IDestinationResolver(inbound)
        self.assertEquals(IUUID(context), resolver.uuid())


class TestMailIn(PloneTestCase):

    layer = Layer

    def set_up_content(self):
        self.folder.invokeFactory('Folder', 'f1', title='Test Folder')
        f1 = self.folder['f1']
        view = f1.restrictedTraverse('@@mail-in')
        return f1, view

    def test_mailin_email(self):
        obj, view = self.set_up_content()

        expect = "%s@example.org" % IUUID(obj)
        self.assertEquals(expect, view.email())

    def test_mailin_title(self):
        obj, view = self.set_up_content()

        expect = "Mail-In of Test Folder"
        self.assertEquals(expect, view.title())


