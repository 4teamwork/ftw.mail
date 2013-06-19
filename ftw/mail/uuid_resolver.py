from ftw.mail.interfaces import IMailSettings
from plone.app.uuid.utils import uuidToObject
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility


class DestinationFromUUID(object):
    """UUID resolver
    """

    def __init__(self, inbound):
        self.inbound = inbound

    def uuid(self):
        return self.inbound.recipient().split('@')[0]

    def destination(self):
        return uuidToObject(self.uuid())

    def email(self):
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        domain = getattr(proxy, 'mail_domain', 'nodomain.com')
        return '%s@%s' % (self.uuid(), domain)
