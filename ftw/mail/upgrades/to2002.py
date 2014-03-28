from ftw.upgrade import UpgradeStep
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class RemoveValidateSender(UpgradeStep):

    def __call__(self):
        registry = getUtility(IRegistry)
        key = 'ftw.mail.interfaces.IMailSettings.validate_sender'
        del registry.records[key]
