from AccessControl import Unauthorized
from ftw.mail import exceptions
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from email.Utils import parseaddr
from ftw.mail import utils
from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IMailInbound
from ftw.mail.interfaces import IMailSettings
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from z3c.form.interfaces import IValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.schema import getFields
from zope.schema import getFieldsInOrder
from zope.security.interfaces import IPermission
import email


class MailInbound(BrowserView):
    """ A view that handles inbound mail posted by mta2plone.py
    """

    implements(IMailInbound)

    def __call__(self):
        return self.render()

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
        destination = self.get_destination()
        if user is None:
            # if we couldn't get a member from the sender address,
            # use the owner of the container to create the mail object
            user = destination.getWrappedOwner()

        sm = getSecurityManager()
        newSecurityManager(self.request, user)
        try:
            createMailInContainer(destination, msg.as_string())
        except Unauthorized:
            raise exceptions.PermissionDenied(self.msg(), user)
        except ValueError:
            raise exceptions.DisallowedSubobjectType(self.msg(), user)
        finally:
            setSecurityManager(sm)

    def get_user(self):
        settings = getUtility(IRegistry).forInterface(IMailSettings)
        sender_email = self.sender()

        if settings.validate_sender and not sender_email:
            raise exceptions.NoSenderFound(self.msg())

        elif not sender_email:
            return None

        acl_users = getToolByName(self.context, 'acl_users')
        pas_search = getMultiAdapter((self.context, self.request),
                                     name='pas_search')
        users = pas_search.searchUsers(email=sender_email)
        if len(users) > 0:
            user = acl_users.getUserById(users[0].get('userid'))
            if not hasattr(user, 'aq_base'):
                user = user.__of__(acl_users)
            return user
        elif settings.validate_sender:
            raise exceptions.UnkownSender(self.msg())
        else:
            return None

    def get_destination(self):
        emailaddress = IEmailAddress(self.request)
        destination = emailaddress.get_object_for_email(self.recipient())

        if destination is None:
            raise exceptions.DestinationDoesNotExist(emailaddress)
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

    # lookup the type of the 'message' field and create an instance
    fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
    schema = fti.lookupSchema()
    field_type = getFields(schema)['message']._type
    message_value = field_type(data=message,
                       contentType=u'message/rfc822', filename=u'message.eml')
    # create mail object
    content = createContent('ftw.mail.mail', message=message_value)

    container = aq_inner(container)
    container_fti = container.getTypeInfo()

    # check permission
    permission = queryUtility(IPermission, name='ftw.mail.AddInboundMail')
    if permission is None:
        raise Unauthorized("Cannot create %s" % content.portal_type)
    if not getSecurityManager().checkPermission(permission.title, container):
        raise Unauthorized("Cannot create %s" % content.portal_type)

    # check addable types
    if container_fti is not None and \
            not container_fti.allowType(content.portal_type):
        raise ValueError("Disallowed subobject type: %s" % (
                content.portal_type))

    normalizer = queryUtility(IIDNormalizer)
    normalized_subject = normalizer.normalize(content.title)

    name = INameChooser(container).chooseName(normalized_subject, content)
    content.id = name

    newName = container._setObject(name, content)
    obj = container._getOb(newName)
    obj = set_defaults(obj)
    obj.reindexObject()
    return obj


def set_defaults(obj):
    """set the default value for all fields on the mail object
    (including additional behaviors)"""

    for schemata in iterSchemata(obj):
        for name, field in getFieldsInOrder(schemata):
            if field.get(field.interface(obj)) == field.missing_value \
                or field.get(field.interface(obj)) is None:

                # No value is set, so we try to set the default value
                # otherwise we set the missing value
                default = queryMultiAdapter((
                        obj,
                        obj.REQUEST,  # request
                        None,  # form
                        field,
                        None,  # Widget
                        ), IValue, name='default')
                if default is not None:
                    default = default.get()
                if default is None:
                    default = getattr(field, 'default', None)
                if default is None:
                    try:
                        default = field.missing_value
                    except:
                        pass
                field.set(field.interface(obj), default)
    return obj
