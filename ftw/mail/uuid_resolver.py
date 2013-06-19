from plone.app.uuid.utils import uuidToObject


class DestinationFromUUID(object):
    """UUID resolver
    """

    def __init__(self, inbound):
        self.inbound = inbound

    def uuid(self):
        return self.inbound.recipient().split('@')[0]

    def destination(self):
        return uuidToObject(self.uuid())
