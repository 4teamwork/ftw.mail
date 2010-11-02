from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from email.MIMEText import MIMEText
from five import grok
from ftw.mail import _
from ftw.mail import utils
from plone.dexterity.content import Item
from plone.directives import form
from plone.memoize import instance
from plone.namedfile import field
import email


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
