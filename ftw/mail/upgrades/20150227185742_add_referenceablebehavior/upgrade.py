from ftw.upgrade import UpgradeStep
from Products.Archetypes import config


class AddReferenceablebehavior(UpgradeStep):
    """Add referenceablebehavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
        msg = 'Update UID catalog after enabling referenceablebehavior on mails.'
        uidcatalog = self.getToolByName(config.UID_CATALOG)
        for mail in self.objects({'portal_type': 'ftw.mail.mail'}, msg):
            uidcatalog.catalog_object(mail, '/'.join(mail.getPhysicalPath()))
