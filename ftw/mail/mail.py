import email
from email.MIMEText import MIMEText
from Acquisition import aq_inner
from five import grok
from zope import schema
from plone.directives import form, dexterity
from plone.namedfile.field import NamedFile
from plone.dexterity.content import Item
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from ftw.mail import _
from ftw.mail import utils


class IMail(form.Schema):
    """An e-mail message.
    """

    form.primary('message')
    message = NamedFile(
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
            return subject.decode('utf8')
        return _(u'no_subject',default=u'[No Subject]')

    def setTitle(self, value):
        pass

    @property
    @instance.memoize
    def msg(self):
        """ returns an email.Message instance
        """
        if self.message:
            return email.message_from_string(self.message.data)
        return MIMEText('')

class View(grok.View):
    """
    """
    grok.context(IMail)
    grok.require('zope2.View')

    def get_header(self, name):
        context = aq_inner(self.context)
        return utils.get_header(context.msg, name)

    def get_date_header(self, name):
        context = aq_inner(self.context)
        return DateTime(utils.get_date_header(context.msg, name))

    def body(self):
        context = aq_inner(self.context)
        html_body = utils.get_body(context.msg, context.absolute_url())
        return utils.unwrap_html_body(html_body, 'mailBody')

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

