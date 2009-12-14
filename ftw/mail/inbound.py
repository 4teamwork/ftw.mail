import email
from five import grok
from Acquisition import aq_inner
from ftw.mail import utils
from zExceptions import NotFound
from ftw.mail.mail import IMail
from Products.CMFCore.interfaces import ISiteRoot


class MailInbound(grok.CodeView):
    """ A view that handles inbound mail posted by mta2plone.py
    """
    grok.context(ISiteRoot)
    grok.require('zope2.View')
    grok.name('mail-inbound')
    
    def render(self):
        context = aq_inner(self.context)
        message_txt = self.request.get('mail', None)
        
        if message_txt is None:
            raise IOError, 'No mail message supplied.'
        try:
            message = email.message_from_string(message_txt)
        except TypeError:
            raise IOError, 'Invalid mail message supplied.'
            
        