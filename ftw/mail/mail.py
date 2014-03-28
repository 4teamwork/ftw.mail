from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective import dexteritytextindexer
from email.MIMEText import MIMEText
from ftw.mail import _
from ftw.mail import utils
from plone.dexterity.content import Item
from plone.directives import form
from plone.memoize import instance
from plone.namedfile import field
from zope.interface import implements
import email


class IMail(form.Schema):
    """An e-mail message.
    """

    form.primary('message')
    message = field.NamedBlobFile(
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

    @title.setter
    def title(self, value):
        """Since the title of an e-Mail can't be changed (it's always
        what the subject of the message contains), this is a dummy setter.
        It is still needed though, because otherwise plone.dexterity.utils
        fails in createContent() when trying to set attributes on the newly
        created content object.
        """
        pass

    @property
    def msg(self):
        """ returns an email.Message instance
        """
        if self.message is not None:
            data = self.message.data
            temp_msg = email.message_from_string(data)
            if temp_msg.get('Subject') and '\n\t' in temp_msg['Subject']:
                # It's a long subject header than has been separated by
                # line break and tab - fix it
                fixed_subject = temp_msg['Subject'].replace('\n\t', ' ')
                data = data.replace(temp_msg['Subject'], fixed_subject)
            return email.message_from_string(data)
        return MIMEText('')


# SearchableText
class SearchableTextExtender(object):
    """This DynamicTextIndexExtender decodes the body of e-Mail messages
    and adds it to the searchableText.
    """

    implements(dexteritytextindexer.IDynamicTextIndexExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        transforms = getToolByName(self.context, 'portal_transforms')

        def convert_to_text(msg):
            if msg.is_multipart():
                result = map(convert_to_text, msg.get_payload())
                result = filter(None, result)
                return ' '.join(result)

            result = transforms.convertTo('text/plain',
                                          msg.get_payload(decode=True),
                                          mimetype=msg.get_content_type(),
                                          filename=msg.get_filename())

            if not result:
                return None

            result = result.getData().strip()

            if isinstance(result, unicode):
                return result.encode('utf-8')
            else:
                return result

        return convert_to_text(self.context.msg)


class View(BrowserView):
    """Default view for mail content type
    """

    template = ViewPageTemplateFile('mail_templates/view.pt')

    def __call__(self):
        return self.template()

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
