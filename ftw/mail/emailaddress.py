from ftw.mail.interfaces import IEmailAddress
from ftw.mail.interfaces import IMailSettings
from plone.app.uuid.utils import uuidToObject
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.component import queryUtility
from zope.interface import implements


class UUIDEmailAddress(object):
    implements(IEmailAddress)

    def __init__(self, request):
        self.request = request

    def get_email_for_object(self, obj, domain=None):
        if domain is None:
            registry = queryUtility(IRegistry)
            proxy = registry.forInterface(IMailSettings)
            domain = getattr(proxy, 'mail_domain', u'nodomain.com').encode(
            'utf-8')

        return '@'.join((IUUID(obj), domain))

    def get_object_for_email(self, email):
        uuid = email.split('@')[0]
        return uuidToObject(uuid)
