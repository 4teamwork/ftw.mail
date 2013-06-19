from plone.app.uuid.utils import uuidToObject


class DestinationFromUUID(object):
    """UUID resolver
    """

    def __init__(self, context):
        self.context = context

    def destination(self):
        uuid = self.context.recipient().split('@')[0]
        return uuidToObject(uuid)
