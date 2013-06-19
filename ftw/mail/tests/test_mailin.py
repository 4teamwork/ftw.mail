from ftw.mail.tests.layer import Layer
from plone.uuid.interfaces import IUUID
from Products.PloneTestCase.ptc import PloneTestCase


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


