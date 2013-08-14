from ftw.mail.emailaddress import UUIDEmailAddress
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.interface.verify import verifyClass
from zope.publisher.browser import TestRequest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestUUIDResolver(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer.get('portal')

        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])

        self.portal.invokeFactory('Folder', 'f1')
        self.subfolder = self.portal['f1']

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
