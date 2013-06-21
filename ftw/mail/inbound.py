from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Acquisition import aq_inner
from email.Utils import parseaddr
from ftw.mail import utils
from ftw.mail.config import EXIT_CODES
from ftw.mail.interfaces import IMailInbound, IMailSettings
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from z3c.form.interfaces import IValue
from zope.container.interfaces import INameChooser
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.component import queryMultiAdapter
from zope.interface import implements
from ftw.mail.interfaces import IEmailAddress
from zope.schema import getFields
from zope.schema import getFieldsInOrder
from zope.security.interfaces import IPermission
import email


class MailInboundException(Exception):
    """ An exception indicating an error occured while processing
        an inbound mail.
    """
    def __init__(self, exitcode, errormsg):
        self.exitcode = exitcode
        self.errormsg = errormsg
    def __str__(self):
        return '%s:%s' % (self.exitcode, self.errormsg)


class MailInbound(BrowserView):
    """ A view that handles inbound mail posted by mta2plone.py
    """

    implements(IMailInbound)

    def __call__(self):
        return self.render()

    def render(self):
        context = aq_inner(self.context)

        registry = getUtility(IRegistry)
        reg_proxy = registry.forInterface(IMailSettings)
        validate_sender = reg_proxy.validate_sender
        unwrap_mail = reg_proxy.unwrap_mail

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

            msg = self.msg()
            # if we find an attached mail, use this instead of the whole one
            if unwrap_mail:
                msg = utils.unwrap_attached_msg(msg)

            msg_txt = msg.as_string()

            sm = getSecurityManager()
            newSecurityManager(self.request, user)

            try:
                destination = self.get_destination()

                # if we couldn't get a member from the sender address,
                # use the owner of the container to create the mail object
                if user is None:
                    user = destination.getWrappedOwner()

                try:
                    createMailInContainer(destination, msg_txt)
                except Unauthorized:
                    raise MailInboundException(EXIT_CODES['NOPERM'],
                          'Unable to create message. Permission denied.')
                except ValueError:
                    raise MailInboundException(EXIT_CODES['NOPERM'],
                          'Disallowed subobject type. Permission denied.')
            finally:
                setSecurityManager(sm)

        except MailInboundException, e:
            return str(e)

        return '0:OK'

    def get_destination(self):
        emailaddress = IEmailAddress(self.request)
        destination = emailaddress.get_object_for_email(self.recipient())

        if destination is None:
            raise MailInboundException(EXIT_CODES['CANTCREAT'],
                                       'Destination does not exist.')
        return destination

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
    if container_fti is not None and not container_fti.allowType(content.portal_type):
        raise ValueError("Disallowed subobject type: %s" % content.portal_type)

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
