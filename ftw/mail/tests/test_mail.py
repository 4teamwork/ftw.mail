from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.rfc822.interfaces import IPrimaryFieldInfo
from unittest2 import TestCase
from zExceptions import NotFound
from zope.component import createObject
from zope.component import queryUtility
import os


class TestMailIntegration(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestMailIntegration, self).setUp()

        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])

        here = os.path.dirname(__file__)
        self.msg_txt_attachment = open(
            os.path.join(here, 'mails', 'attachment.txt'), 'r').read()

    def test_adding(self):
        mail = create(Builder('mail'))
        self.failUnless(IMail.providedBy(mail))

        self.assertEquals(u'no_subject', mail.title)

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
        mail = create(Builder('mail'))

        mail.REQUEST.set('ACTUAL_URL', mail.absolute_url())
        view = mail.restrictedTraverse('@@view')
        view()

        self.assertEquals('', view.get_header('Subject'))
        self.assertEquals('<div class="mailBody"></div>', view.body())

    def test_attachments(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_txt_attachment))

        mail.REQUEST.set('ACTUAL_URL', mail.absolute_url())
        view = mail.restrictedTraverse('@@view')
        view()

        attachments = view.attachments()
        self.assertEquals(1, len(attachments))
        self.failUnless('icon' in attachments[0])

    def test_get_attachment(self):
        mail = create(Builder('mail'))

        view = mail.restrictedTraverse('@@get_attachment')
        self.assertRaises(NotFound, view)

    def test_setting_title(self):
        # Try setting the title property
        # This is not supposed to change the title,
        # since that is always read from the subject,
        # but it shouldn't fail with an AttributeError

        mail = create(Builder('mail'))
        self.assertEquals(u'no_subject', mail.title)

        mail.title = "New Title"
        self.assertEquals(u'no_subject', mail.title)

    def test_message_field_is_marked_as_primary_field(self):
        mail = create(Builder('mail'))
        self.assertEquals(IMail['message'], IPrimaryFieldInfo(mail).field)

    # def test_special(self):
    #     here = os.path.dirname(__file__)
    #     msg_txt = open(os.path.join(here, 'mails', 'cipra.txt'), 'r').read()
    #     fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
    #     schema = fti.lookupSchema()
    #     field_type = getFields(schema)['message']._type
    #     obj = createContentInContainer(self.portal, 'ftw.mail.mail',
    #                message=field_type(data=msg_txt,
    #                contentType='message/rfc822', filename='message.eml'))
    #     m1 = self.portal[obj.getId()]
    #     view = m1.restrictedTraverse('@@view')
    #     view()
