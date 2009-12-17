import email
from Acquisition import aq_inner
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from AccessControl import Unauthorized
from email.Utils import parseaddr
from five import grok
from ftw.mail import utils
from ftw.mail.interfaces import IMailInbound, IDestinationResolver
from ftw.mail.mail import IMail
from plone.dexterity.utils import createContentInContainer
from plone.memoize import instance
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.component import getMultiAdapter, getUtility
from zope.interface import implements
from zope.intid.interfaces import IIntIds
from zope.schema import getFields
from plone.dexterity.interfaces import IDexterityFTI
from ftw.mail.config import EXIT_CODES


class MailInboundException(Exception):
    """ An exception indicating an error occured while processing
        an inbound mail.
    """
    def __init__(self, exitcode, errormsg):
        self.exitcode = exitcode
        self.errormsg = errormsg
    def __str__(self):
        return '%s:%s' % (self.exitcode, self.errormsg)


class MailInbound(grok.CodeView):
    """ A view that handles inbound mail posted by mta2plone.py
    """
    grok.context(ISiteRoot)
    grok.require('zope2.View')
    grok.name('mail-inbound')
    implements(IMailInbound)
    
    def render(self):
        context = aq_inner(self.context)
        validate_sender = True
        
        try:
            user = None
            sender_email = self.sender()

            if validate_sender and not sender_email:
                raise MailInboundException(EXIT_CODES['NOPERM'], 
                      'Unknown sender. Permission denied.')
                        
            # get portal member by sender address
            if sender_email:
                pas_search = getMultiAdapter((context, self.request), name='pas_search')
                users = pas_search.searchUsers(email=sender_email)
                if len(users)>0:
                    portal = getToolByName(context, 'portal_url').getPortalObject()
                    uf = portal.acl_users
                    user = uf.getUserById(users[0].get('userid'))
                    if not hasattr(user, 'aq_base'):
                        user = user.__of__(uf)
                    #member = mtool.getMemberById(users[0].get('userid'))
            
            if validate_sender and user is None:
                raise MailInboundException(EXIT_CODES['NOPERM'], 
                      'Unknown sender. Permission denied.')

            # if we find an attached mail, use this instead of the whole one
            msg = self.msg()
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'message/rfc822':
                        msg = part.get_payload(0)
                        break

            # get destination container
            resolver = IDestinationResolver(self)
            destination = resolver.destination()

            if destination is None:
                raise MailInboundException(EXIT_CODES['CANTCREAT'], 
                                           'Destination does not exist.')
            if destination:
                subject = utils.get_header(self.msg(), 'Subject') or '[No Subject]'
                # if we couldn't get a member from the sender address,
                # use the owner of the container to create the mail object
                if user is None:
                    user = destination.getWrappedOwner()

                # lookup the type of the 'message' field and create an instance
                fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
                schema = fti.lookupSchema()
                field_type = getFields(schema)['message']._type
                message_value = field_type(data=msg.as_string(),
                       contentType='message/rfc822', filename='message.eml')

                newSecurityManager(self.request, user)
                try:
                    createContentInContainer(destination, 'ftw.mail.mail', message=message_value)
                except Unauthorized:
                    raise MailInboundException(EXIT_CODES['NOPERM'], 
                          'Unable to create message. Permission denied.')
                noSecurityManager()

        except MailInboundException, e:
            return str(e)

        return '0:OK'

    @instance.memoize
    def msg(self):
        """ create an email.Message instance from request.
        """
        msg_txt = self.request.get('mail', None)
        if msg_txt is None:
            raise MailInboundException(EXIT_CODES['NOINPUT'], 
                                       'No mail message supplied.')
        try:
            msg = email.message_from_string(msg_txt)
        except TypeError:
            raise MailInboundException(EXIT_CODES['DATAERR'], 
                                       'Invalid mail message supplied.')
        return msg

    @instance.memoize
    def sender(self):
        """ get the email address of the sender
        """
        sender = utils.get_header(self.msg(), 'Resent-From')
        if not sender:
            sender = utils.get_header(self.msg(), 'From')
        (sender_name, sender_address) = parseaddr(sender)
        return sender_address

    @instance.memoize        
    def recipient(self):
        """ get the email address of the recipient
        """
        recipient = utils.get_header(self.msg(), 'Resent-To')
        if not recipient:
            recipient = utils.get_header(self.msg(), 'To')
        (recipient_name, recipient_address) = parseaddr(recipient)
        return recipient_address

# class DestinationFromLocalPart(grok.Adapter):
#     """ A destination resolver that  
#     """
#     grok.provides(IDestinationResolver)
#     grok.context(IMailInbound)
#     #grok.name(u'path-from-local-part')
# 
#     def destination(self):
#         parts = self.context.recipient().split('@')
#         path = parts[0].replace('.', '/')
#         context = aq_inner(self.context.context)
#         portal_path = getToolByName(context, 'portal_url').getPortalPath()
#         destination = None
#         try:
#             destination = context.unrestrictedTraverse('%s/%s' % (portal_path, path))
#         except KeyError:
#             pass
#         return destination

class DestinationFromIntId(grok.Adapter):
    """ An intid resolver
    """
    grok.provides(IDestinationResolver)
    grok.context(IMailInbound)
    #grok.name(u'intid')
    
    def destination(self):
        intid = self.context.recipient().split('@')[0]
        id_util = getUtility(IIntIds)
        try:
            intid = int(intid)
        except ValueError:
            return None
        return id_util.queryObject(intid)


    