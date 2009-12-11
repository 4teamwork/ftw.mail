from five import grok
from zope import schema

from plone.directives import form, dexterity

from plone.app.textfield import RichText
from plone.namedfile.field import NamedFile
from plone.dexterity.content import Item

from ftw.mail import _
from ftw.mail import utils

class IMail(form.Schema):
    """An e-mail message.
    """

    mail_subject = schema.TextLine(
        title = _(u"Subject"),
        required = False,
        readonly = True,
    )
    
    mail_from = schema.TextLine(
        title = _(u"From"),
        required = False,
    ) 

    mail_to = schema.TextLine(
        title = _(u"To"),
        required = False,
    )
    
    mail_cc = schema.TextLine(
        title = _(u"Cc"),
        required = False,
    )
    
    mail_date = schema.Datetime(
        title = _(u"Date"),
        required = False,
    )
    
    mail_body = RichText(
        title = _(u"Body"),
        required = False,
    )

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
        return self.mail_subject or '[No Subject]'
    
    def setTitle(self, value):
        pass

    @property
    def mail_subject(self):
        return utils.get_header(self.message, 'Subject')
