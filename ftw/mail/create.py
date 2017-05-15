from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from ftw.mail.interfaces import ICreateMailInContainer
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent
from plone.dexterity.utils import iterSchemata
from plone.i18n.normalizer.interfaces import IIDNormalizer
from z3c.form.interfaces import IValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.schema import getFields
from zope.schema import getFieldsInOrder
from zope.security.interfaces import IPermission


class CreateMailInContainer(object):
    implements(ICreateMailInContainer)

    portal_type = 'ftw.mail.mail'

    def __init__(self, context, request):
        self.context = aq_inner(context)
        self.request = request

    def create_mail(self, message):
        """Add a mail object to a container.

        The new object, wrapped in its new acquisition context, is returned.
        """

        self.check_permission()
        self.check_addable_types()

        content = self.create_mail_object(message)
        name = self.choose_name(content)
        obj = self.add_to_container(name, content)

        self.set_defaults(obj)
        return obj

    def check_permission(self):
        permission = queryUtility(IPermission, name='ftw.mail.AddInboundMail')
        if permission is None:
            raise Unauthorized("Cannot create %s" % self.portal_type)
        if not getSecurityManager().checkPermission(permission.title,
                                                    self.context):
            raise Unauthorized("Cannot create %s" % self.portal_type)

    def check_addable_types(self):
        container_fti = self.context.getTypeInfo()
        if container_fti is not None and \
                not container_fti.allowType(self.portal_type):
            raise ValueError("Disallowed subobject type: %s" % (
                self.portal_type))

    def create_mail_object(self, message):
        # lookup the type of the 'message' field and create an instance
        fti = getUtility(IDexterityFTI, name=self.portal_type)
        schema = fti.lookupSchema()
        field_type = getFields(schema)['message']._type
        message_value = field_type(
            data=message,
            contentType='message/rfc822', filename=u'message.eml')

        # create content object
        content = createContent(self.portal_type, message=message_value)
        return content

    def choose_name(self, content):
        normalizer = queryUtility(IIDNormalizer)
        normalized_subject = normalizer.normalize(content.title)

        name = INameChooser(self.context).chooseName(
            normalized_subject, content)
        content.id = name
        return name

    def add_to_container(self, name, content):
        newName = self.context._setObject(name, content)
        obj = self.context._getOb(newName)
        return obj

    def set_defaults(self, obj):
        """set the default value for all fields on the mail object
        (including additional behaviors)"""

        for schema in iterSchemata(obj):
            for name, field in getFieldsInOrder(schema):
                # Remove acquisition wrapper when getting field value so
                # determining if a field is already set works as expected
                value = field.get(field.interface(aq_base(obj)))
                if value == field.missing_value or value is None:
                    # bind the field for choices with named vocabularies
                    field = field.bind(obj)

                    # No value is set, so we try to set the default value
                    # otherwise we set the missing value
                    default = queryMultiAdapter((
                            self.context,
                            self.request,  # request
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

        obj.reindexObject()
