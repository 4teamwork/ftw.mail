from zope.component import createObject
from zope.component import queryUtility
from plone.dexterity.interfaces import IDexterityFTI
from Products.PloneTestCase.ptc import PloneTestCase
from zExceptions import NotFound
from ftw.mail.tests.layer import Layer
from ftw.mail.mail import IMail


class TestMailIntegration(PloneTestCase):

    layer = Layer

    def test_adding(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        self.failUnless(IMail.providedBy(m1))
        self.assertEquals('[No Subject]', m1.title)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='ftw.mail.mail')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='ftw.mail.mail')
        schema = fti.lookupSchema()
        self.assertEquals(IMail, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='ftw.mail.mail')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IMail.providedBy(new_object))
        self.assertEquals('[No Subject]', new_object.title)

    def test_view(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        view = m1.restrictedTraverse('@@view')
        view.update()
        subject = view.get_header('Subject')
        self.assertEquals('', subject)
        body = view.body()
        self.assertEquals('', body)

    def test_attachment(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        view = m1.restrictedTraverse('@@get_attachment')
        self.assertRaises(NotFound, view)
