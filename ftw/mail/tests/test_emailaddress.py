from ftw.mail.interfaces import IEmailAddress
from ftw.mail.tests.layer import Layer
from plone.uuid.interfaces import IUUID
from Products.PloneTestCase.ptc import PloneTestCase
from zope.interface.verify import verifyClass
from zope.publisher.browser import TestRequest
from ftw.mail.emailaddress import UUIDEmailAddress


class TestUUIDResolver(PloneTestCase):

    layer = Layer

    def afterSetUp(self):
        self.folder.invokeFactory('Folder', 'f1')
        self.subfolder = self.folder['f1']

        self.request = TestRequest()
        self.emailaddress = IEmailAddress(self.request)

    def test_verify_adapter(self):
        verifyClass(IEmailAddress, UUIDEmailAddress)

    def test_get_object_for_email(self):
        email = "%s@example.org" % IUUID(self.subfolder)

        self.assertEquals(self.subfolder,
                          self.emailaddress.get_object_for_email(email))

    def test_get_email_for_object(self):
        email = "%s@example.org" % IUUID(self.subfolder)
        self.assertEquals(
            email,
            self.emailaddress.get_email_for_object(self.subfolder))

    def test_get_email_for_object_with_different_domain(self):
        email = "%s@otherdomain.org" % IUUID(self.subfolder)
        self.assertEquals(
            email,
            self.emailaddress.get_email_for_object(self.subfolder,
                                                   'otherdomain.org'))
