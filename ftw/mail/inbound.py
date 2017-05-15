from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from email.Utils import parseaddr
from ftw.mail import exceptions
from ftw.mail import utils
from ftw.mail.interfaces import ICreateMailInContainer
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IInboundRequest
from ftw.mail.interfaces import IMailInbound
from ftw.mail.interfaces import IMailSettings
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides
import email


class MailInbound(BrowserView):
    """ A view that handles inbound mail posted by mta2plone.py
    """

    implements(IMailInbound)

    def __call__(self):
        alsoProvides(self.request, IInboundRequest)
        result = self.render()
        noLongerProvides(self.request, IInboundRequest)
        return result

    def render(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        try:
            self.inbound()
            return '0:OK'
        except exceptions.MailInboundException, e:
            return str(e)

    def inbound(self):
        msg = self.msg()
        settings = getUtility(IRegistry).forInterface(IMailSettings)
        if settings.unwrap_mail:
            # if we find an attached mail, use this instead of the whole one
            msg = utils.unwrap_attached_msg(msg)

        user = self.get_user()
        sm = getSecurityManager()
        newSecurityManager(self.request, user)
        try:
            destination = self.get_destination()
            createMailInContainer(destination, msg.as_string())
        except Unauthorized:
            raise exceptions.PermissionDenied(self.msg(), user)
        except ValueError:
            raise exceptions.DisallowedSubobjectType(self.msg(), user)
        finally:
            setSecurityManager(sm)

    def get_user(self):
        sender_email = self.sender()
        if not sender_email:
            raise exceptions.NoSenderFound(self.msg())

        acl_users = getToolByName(self.context, 'acl_users')
        pas_search = getMultiAdapter((self.context, self.request),
                                     name='pas_search')
        users = pas_search.searchUsers(email=sender_email)
        if len(users) > 0:
            user = acl_users.getUserById(users[0].get('userid'))
            if not hasattr(user, 'aq_base'):
                user = user.__of__(acl_users)
            return user
        else:
            raise exceptions.UnknownSender(self.msg())

    def get_destination(self):
        emailaddress = IEmailAddress(self.request)
        destination = emailaddress.get_object_for_email(self.recipient())

        if destination is None:
            raise exceptions.DestinationDoesNotExist(self.recipient())
        return destination

    @instance.memoize
    def msg(self):
        """ create an email.Message instance from request.
        """
        msg_txt = self.request.get('mail', None)
        if msg_txt is None:
            raise exceptions.NoInput()
        try:
            msg = email.message_from_string(msg_txt)
        except TypeError:
            raise exceptions.InvalidMessage()
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
        # If recipient is supplied in request (by mta2plone), use that
        recipient = self.request.get('recipient')
        if not recipient:
            # Otherwise fall back to `Resent-To` or `To` headers
            recipient = utils.get_header(self.msg(), 'Resent-To')
            if not recipient:
                recipient = utils.get_header(self.msg(), 'To')
        (recipient_name, recipient_address) = parseaddr(recipient)
        return recipient_address


def createMailInContainer(container, message):
    """Add a mail object to a container.

    The new object, wrapped in its new acquisition context, is returned.
    """
    creator = getMultiAdapter((container, container.REQUEST),
                              ICreateMailInContainer)
    return creator.create_mail(message)
