import email
from five import grok
from Acquisition import aq_inner
from ftw.mail import utils
from zExceptions import NotFound
from ftw.mail.mail import IMail

class AttachmentView(grok.CodeView):
    """Returns the attachment at the position specified in the request.
    """
    grok.context(IMail)
    grok.require('zope2.View')
    grok.name('get_attachment')

    def update(self):
        context = aq_inner(self.context)
        self.message = context.message
        self.position = self.request.get('position', '0')
    
    def render(self):

        if self.message is None:
            raise NotFound
        message = email.message_from_string(self.message.data)

        # we need an int value for the position
        pos = 0
        try:
            pos = int(self.position)
        except ValueError:
            raise NotFound

        # get attachment at position pos
        attachment = None
        for i, part in enumerate(message.walk()):
            if i == pos:
                attachment = part
                continue

        if attachment is not None:
            content_type = attachment.get_content_type()
            filename = utils.get_filename(attachment)
            if filename is None:
                raise NotFound
            # make sure we have a unicode string
            if not isinstance(filename, unicode):
                filename = filename.decode('utf-8', 'ignore')
            # internet explorer and safari don't like rfc encoding of filenames
            # and they don't like utf encoding too.
            # therefore we first try to encode the filename in iso-8859-1
            try:    
                filename = filename.encode('iso-8859-1')
            except:
                filename = filename.encode('utf-8', 'ignore')
                
            self.request.response.setHeader('Content-Type', content_type)
            self.request.response.setHeader('Content-Disposition', 'inline; filename=%s' % filename)

            if content_type == 'message/rfc822':
                return attachment.as_string()
            return attachment.get_payload(decode=1)
            
        raise NotFound        
