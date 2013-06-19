from email.MIMEText import MIMEText
from ftw.mail.interfaces import IMailInbound, IDestinationResolver
from ftw.mail.tests.layer import Layer
from plone.uuid.interfaces import IUUID
from Products.PloneTestCase.ptc import PloneTestCase
from zope.interface import implements


class TestInboundMail(PloneTestCase):

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

    def test_uuid_resolver_email(self):
        context, inbound = self.set_up_dummy_inbound()

        resolver = IDestinationResolver(inbound)
        self.assertEquals(inbound.recipient(), resolver.email())

    def test_uuid_resolver_uuid(self):
        context, inbound = self.set_up_dummy_inbound()

        resolver = IDestinationResolver(inbound)
        self.assertEquals(IUUID(context), resolver.uuid())
