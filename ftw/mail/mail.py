import datetime
import email

from Acquisition import aq_inner, aq_parent
from DateTime import DateTime
from email.MIMEText import MIMEText
from five import grok
from ftw.mail import utils
from ftw.mail import _

from plone.dexterity.content import Item
from plone.directives import form
from plone.memoize import instance
from plone.namedfile import field
from plone.namedfile import NamedFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage


class IMail(form.Schema):
    """An e-mail message.
    """

    form.primary('message')
    message = field.NamedFile(
        title = _(u"label_raw_message", default=u"Raw Message"),
        description = _(u"help_raw_message", default=u""),
        required = False,
    )


class Mail(Item):
    """An e-mail message."""

    @property
    def title(self):
        """get title from subject
        """
        subject = utils.get_header(self.msg, 'Subject')
        if subject:
            # long headers may contain line breaks with tabs.
            # replace these by a space.
            subject = subject.replace('\n\t', ' ')
            return subject.decode('utf8')
        return _(u'no_subject', default=u'[No Subject]')

    def setTitle(self, value):
        pass

    @property
    def msg(self):
        """ returns an email.Message instance
        """
        if self.message is not None:
            return email.message_from_string(self.message.data)
        return MIMEText('')


class View(grok.View):
    """
    """
    grok.context(IMail)
    grok.require('zope2.View')

    def get_header(self, name):
        return utils.get_header(self.msg(), name)

    def get_date_header(self, name):
        return DateTime(utils.get_date_header(self.msg(), name))

    def body(self):
        context = aq_inner(self.context)
        html_body = utils.get_body(self.msg(), context.absolute_url())
        return utils.unwrap_html_body(html_body, 'mailBody')

    @instance.memoize
    def msg(self):
        context = aq_inner(self.context)
        return context.msg

    @instance.memoize
    def attachments(self):
        context = aq_inner(self.context)
        attachments = utils.get_attachments(context.msg)
        mtr = getToolByName(context, 'mimetypes_registry')
        for attachment in attachments:
            icon = 'file_icon.gif'
            type_name = 'File'
            lookup = mtr.lookup(attachment['content-type'])
            if lookup:
                icon = lookup[0].icon_path
                type_name = lookup[0].name()
            attachment['icon'] = icon
            attachment['type-name'] = type_name
        return attachments


class SaveAttachments(View):
    grok.context(IMail)
    grok.name('save_attachments')
    grok.require('zope2.View')
    grok.template('save_attachments')

    def attachments(self):
        context = aq_inner(self.context)
        attachments = utils.get_attachments(context.msg)
        mtr = getToolByName(context, 'mimetypes_registry')
        for attachment in attachments:
            icon = 'file_icon.gif'
            type_name = 'File'
            lookup = mtr.lookup(attachment['content-type'])
            if lookup:
                icon = lookup[0].icon_path
                type_name = lookup[0].name()
            attachment['icon'] = icon
            attachment['type-name'] = type_name
        return attachments

    def __call__(self):
        """ Create a document for each attachment. """
        status = IStatusMessage(self.context.REQUEST)
        attachments = self.context.REQUEST.get('attachment', None)
        count = 0
        if attachments:
            dossier = self.get_parent_dossier()
            for position in attachments:
                count += 1
                attachment = filter(
                    lambda a: str(a['position']) == position,
                    self.attachments())
                if attachment:
                    attachment = attachment[0]
                else:
                    raise Exception(
                        'no attachment with position %s' % position)
                now = DateTime()
                document_id = 'import_%s.%s.%s_%s' % (
                    str(now.strftime('%Y-%m-%d')),
                    str(now.strftime('%M%S')),
                    str(now.millis()),
                    str(position))

                dossier.invokeFactory(
                    'opengever.document.document',
                    document_id,
                    title=attachment['filename'])
                tmp_document = dossier.get(document_id)
                tmp_attachment = None
                for i, part in enumerate(self.context.msg.walk()):
                    if str(i) == position:
                        tmp_attachment = part
                if not tmp_attachment:
                    raise Exception('no attachment found')
                tmp_file = NamedFile(
                    data=tmp_attachment.as_string(),
                    contentType=tmp_attachment.get_content_type(),
                    filename=tmp_attachment.get_filename())

                setattr(tmp_document, 'file', tmp_file)
                setattr(tmp_document, 'document_date', datetime.datetime.now())
                setattr(tmp_document, 'keywords', ())
            if count>1:
                count = "%s Dokumente" % str(count)
            else:
                count = "Dokument"
            status.addStatusMessage(
                u'%s erstellt' % count,
                type='info')
        # delete
        self.delete_attachments()
        return self.template.render(self)

    def delete_attachments(self):
        """deletes the attachments"""
        action = self.context.REQUEST.get('del_attachments', None)
        delete_indexes = []
        delete_messages = []
        if action == 'selected':
            print 'SELECTED'
            delete_indexes = [int(a) for a 
                              in self.context.REQUEST.get('attachment', None)]
        elif action == 'all':
            print 'ALL'
            delete_indexes = [int(a['position']) for a 
                              in self.attachments()]

        new_payload = []
        for i, msg in enumerate(self.context.msg.walk()):
            if i in delete_indexes:
                delete_messages.append(msg)

        for msg in self.context.msg.get_payload():
            if msg not in delete_messages:
                new_payload.append(msg)
        self.context.msg.set_payload(new_payload)
        self.context.message = self.context.msg

    def get_parent_dossier(self):
        """ Get the parent dossier."""
        parent = aq_parent(aq_inner(self.context))
        while parent.portal_type != 'opengever.dossier.businesscasedossier':
            if IPloneSiteRoot.providedBy(parent):
                raise Exception("no dossier found")
            parent = aq_parent(aq_inner(parent))
        return parent
