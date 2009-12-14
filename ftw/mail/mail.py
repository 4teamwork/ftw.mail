import email
from Acquisition import aq_inner
from five import grok
from zope import schema
from plone.directives import form, dexterity
from plone.namedfile.field import NamedFile
from plone.dexterity.content import Item

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
        subject = utils.get_header(self.message, 'Subject')
        return subject or '[No Subject]'

    def setTitle(self, value):
        pass


class View(grok.View):
    """
    """
    grok.context(IMail)
    grok.require('zope2.View')

    def update(self):
        context = aq_inner(self.context)
        self.message = None
        if context.message is not None:
            self.message = email.message_from_string(context.message)

    def get_header(self, name):
        return utils.get_header(self.message, name)
        
    def body(self):
        context = aq_inner(self.context)
        return utils.get_body(self.message, context.absolute_url())
