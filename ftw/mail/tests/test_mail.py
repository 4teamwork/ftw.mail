import os
from zope.component import createObject
from zope.component import queryUtility, getUtility
from zope.schema import getFields
from plone.dexterity.interfaces import IDexterityFTI
from Products.PloneTestCase.ptc import PloneTestCase
from zExceptions import NotFound
from plone.dexterity.utils import createContentInContainer
from ftw.mail.tests.layer import Layer
from ftw.mail.mail import IMail


class TestMailIntegration(PloneTestCase):

    layer = Layer

    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        here = os.path.dirname(__file__)
        self.msg_txt_attachment = open(os.path.join(here, 'mails', 'attachment.txt'), 'r').read()

    def test_adding(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        self.failUnless(IMail.providedBy(m1))
        self.assertEquals(u'no_subject', m1.title)

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
        self.assertEquals(u'no_subject', new_object.title)

    def test_view(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        view = m1.restrictedTraverse('@@view')
        view()
        subject = view.get_header('Subject')
        self.assertEquals('', subject)
        body = view.body()
        self.assertEquals('<div class="mailBody"></div>', body)

    def test_attachments(self):
        # create a mail object containing an attachment
        fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
        schema = fti.lookupSchema()
        field_type = getFields(schema)['message']._type
        obj = createContentInContainer(self.folder, 'ftw.mail.mail',
                   message=field_type(data=self.msg_txt_attachment,
                   contentType=u'message/rfc822', filename=u'message.eml'))
        m1 = self.folder[obj.getId()]
        view = m1.restrictedTraverse('@@view')
        view()
        attachments = view.attachments()
        self.assertEquals(1, len(attachments))
        self.failUnless('icon' in attachments[0])

    def test_get_attachment(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        view = m1.restrictedTraverse('@@get_attachment')
        self.assertRaises(NotFound, view)

    def test_setting_title(self):
        self.folder.invokeFactory('ftw.mail.mail', 'mail1')
        m1 = self.folder['mail1']
        self.assertEquals(u'no_subject', m1.title)
        # Try setting the title property
        # This is not supposed to change the title,
        # since that is always read from the subject,
        # but it shouldn't fail with an AttributeError
        m1.title = "New Title"
        self.assertEquals(u'no_subject', m1.title)


    # def test_special(self):
    #     here = os.path.dirname(__file__)
    #     msg_txt = open(os.path.join(here, 'mails', 'cipra.txt'), 'r').read()
    #     fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
    #     schema = fti.lookupSchema()
    #     field_type = getFields(schema)['message']._type
    #     obj = createContentInContainer(self.folder, 'ftw.mail.mail',
    #                message=field_type(data=msg_txt,
    #                contentType='message/rfc822', filename='message.eml'))
    #     m1 = self.folder[obj.getId()]
    #     view = m1.restrictedTraverse('@@view')
    #     view()
