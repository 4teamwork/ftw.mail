from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective import dexteritytextindexer
from email.MIMEText import MIMEText
from ftw.mail import _
from ftw.mail import utils
from persistent.mapping import PersistentMapping
from plone.dexterity.content import Item
from plone.directives import form
from plone.memoize import instance
from plone.namedfile import field
from plone.rfc822.interfaces import IPrimaryField
from zope.interface import alsoProvides
from zope.interface import implements
import email


class IMail(form.Schema):
    """An e-mail message.
    """

    form.primary('message')
    message = field.NamedBlobFile(
        title=_(u"label_raw_message", default=u"Raw Message"),
        description=_(u"help_raw_message", default=u""),
        required=False,
    )


# necessary for dexterity 1 installations
alsoProvides(IMail['message'], IPrimaryField)


class Mail(Item):
    """An e-mail message."""

    @property
    def title(self):
        default_title = _(u'no_subject', default=u'[No Subject]')
        return getattr(self, '_title', default_title)

    @title.setter
    def title(self, value):
        """Since the title of an e-Mail can't be changed (it's always
        what the subject of the message contains), this is a dummy setter.
        It is still needed though, because otherwise plone.dexterity.utils
        fails in createContent() when trying to set attributes on the newly
        created content object.
        """
        pass

    def _update_title_from_message_subject(self):
        subject = utils.get_header(self.msg, 'Subject')
        if subject:
            # long headers may contain line breaks with tabs.
            # replace these by a space.
            subject = subject.replace('\n\t', ' ')
            self._title = subject.decode('utf8')

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message
        self._update_title_from_message_subject()
        self._update_attachment_infos()
        self._reset_header_cache()

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

    @property
    def attachment_infos(self):
        """A tuple of all attachment, each containing a dict of informations
        for the attachment.

        Example:
        {'position': 4,
        'size': 137588,
        'content-type': 'image/jpg',
        'filename': '1703693_0412c29a4f.jpg'}
        """
        infos = getattr(self, '_attachment_infos', ())
        # Make a copy of each info dict, so that users cannot modify
        # our persistent cache.
        return tuple(map(dict, infos))

    def _update_attachment_infos(self):
        self._attachment_infos = tuple(utils.get_attachments(self.msg))

    def get_header(self, name):
        """Returns a header value from the mail message.
        This method caches the retrieved values.
        """

        if getattr(self, '_header_cache', None) is None:
            self._reset_header_cache()

        if name not in self._header_cache:
            self._header_cache[name] = utils.get_header(self.msg, name)

        return self._header_cache[name]

    def _reset_header_cache(self):
        self._header_cache = PersistentMapping()


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

            # Decode the Content-Transfer-Encoding (QP or base64)
            payload_data = msg.get_payload(decode=True)

            # Decode the actual content
            charset = msg.get_content_charset()
            if charset is not None:
                payload_data = payload_data.decode(charset)
            else:
                # No content charset declared - decode with utf-8
                # and hope for the best, ignoring any decoding errors
                payload_data = payload_data.decode('utf-8', 'ignore')

            # Finally encode it to UTF-8 (transforms require bytestrings)
            payload_data = payload_data.encode('utf-8')

            result = transforms.convertTo('text/plain',
                                          payload_data,
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
        attachments = list(self.context.attachment_infos)
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
