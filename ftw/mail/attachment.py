from Acquisition import aq_inner
from ftw.mail.utils import get_attachment_data
from Products.Five.browser import BrowserView
from zExceptions import NotFound


class AttachmentView(BrowserView):
    """Returns the attachment at the position specified in the request.
    """

    def __call__(self):
        context = aq_inner(self.context)
        self.message = context.message
        self.position = self.request.get('position', '0')

        return self.render()

    def render(self):

        if self.message is None:
            raise NotFound

        # we need an int value for the position
        pos = 0
        try:
            pos = int(self.position)
        except ValueError:
            raise NotFound

        data, content_type, filename = get_attachment_data(self.context.msg, pos)

        if filename is None:
            raise NotFound

        # internet explorer and safari don't like rfc encoding of filenames
        # and they don't like utf encoding too.
        # therefore we first try to encode the filename in iso-8859-1
        try:
            filename = filename.encode('iso-8859-1')
        except UnicodeEncodeError:
            filename = filename.encode('utf-8', 'ignore')

        self.set_content_type(content_type, filename)
        self.set_content_disposition(content_type, filename)
        return data

    def set_content_type(self, content_type, filename):
        self.request.response.setHeader('Content-Type', content_type)

    def set_content_disposition(self, content_type, filename):
        self.request.response.setHeader('Content-Disposition', 'inline; filename=%s' % filename)
