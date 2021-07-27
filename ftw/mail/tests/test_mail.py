from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.namedfile import NamedBlobFile
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import NotFound
from zope.component import createObject
from zope.component import queryUtility
import email
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
        self.msg_utf8 = open(
            os.path.join(here, 'mails', 'utf8.txt'), 'r').read()
        self.msg_invalid_date = open(
            os.path.join(here, 'mails', 'invalid_date.txt'), 'r').read()
        self.msg_timezone_date = open(
            os.path.join(here, 'mails', 'time_zone_dates.txt'), 'r').read()
        self.msg_fwd_attachment = open(
            os.path.join(here, 'mails', 'fwd_attachment.txt'), 'r').read()

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

    def test_attachment_info(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_txt_attachment))

        self.assertEquals(
            ({'position': 1,
              'size': 7,
              'content-type': 'text/plain',
              'filename': 'B\xc3\xbccher.txt'}, ),
            mail.attachment_infos)

    def test_attachment_info_dict_mutations_are_not_stored(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_txt_attachment))

        infos = mail.attachment_infos
        self.assertEquals(
            ({'position': 1,
              'size': 7,
              'content-type': 'text/plain',
              'filename': 'B\xc3\xbccher.txt'}, ),
            infos)
        infos[0]['FOO'] = 'BAR'
        infos[0]['filename'] = 'BAZ'

        self.assertEquals(
            ({'position': 1,
              'size': 7,
              'content-type': 'text/plain',
              'filename': 'B\xc3\xbccher.txt'}, ),
            mail.attachment_infos)

    def test_view(self):
        mail = create(Builder('mail'))

        mail.REQUEST.set('ACTUAL_URL', mail.absolute_url())
        view = mail.restrictedTraverse('@@view')
        view()

        self.assertEquals('', view.get_header('Subject'))
        self.assertEquals('', view.html_safe_body())

    def test_attachments(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_txt_attachment))

        mail.REQUEST.set('ACTUAL_URL', mail.absolute_url())
        view = mail.restrictedTraverse('@@view')
        view()

        attachments = view.attachments()
        self.assertEquals(1, len(attachments))
        self.failUnless('icon' in attachments[0])

    def test_get_missing_attachment(self):
        mail = create(Builder('mail'))

        view = mail.restrictedTraverse('@@get_attachment')
        self.assertRaises(NotFound, view)

    def test_get_eml_attachment(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_fwd_attachment))

        mail.REQUEST.set('position', '2')
        view = mail.restrictedTraverse('@@get_attachment')
        data = view()
        response = mail.REQUEST.response
        self.assertEqual('inline; filename=Lorem Ipsum.eml',
                         response.getHeader("Content-Disposition"))
        self.assertEqual('message/rfc822', response.getHeader('Content-Type'))
        mail = email.message_from_string(data)
        self.assertEqual('from@example.org', mail.get("from"))
        self.assertEqual('to@example.org', mail.get("to"))
        self.assertEqual('Lorem Ipsum', mail.get("Subject"))

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

    def test_header_cache_is_invalidated(self):
        mail = create(Builder('mail')
                      .with_message(self.msg_txt_attachment))
        self.assertEquals('Attachment Test',
                          mail.get_header('Subject'))

        mail.message = NamedBlobFile(
            data=self.msg_utf8,
            contentType='message/rfc822',
            filename=u'message.eml')
        self.assertEquals('Die B\xc3\xbcrgschaft',
                          mail.get_header('Subject'))

    def test_referenceing_mails_from_archetypes_objects(self):
        mail = create(Builder('mail'))
        page = create(Builder('page').having(relatedItems=[IUUID(mail)]))
        self.assertTrue(page)

    def test_date_parsing(self):
        mail = create(Builder('mail').with_message(self.msg_invalid_date))
        self.assertEquals("", mail.get_header('Date', True))
        mail = create(Builder('mail').with_message(self.msg_timezone_date))
        self.assertEquals(DateTime('28.08.2010 18:50:04 GMT+2'),
                          mail.get_header('Date', True))

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
