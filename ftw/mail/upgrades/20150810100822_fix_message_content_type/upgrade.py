from ftw.upgrade import UpgradeStep


class FixMessageContentType(UpgradeStep):
    """Fix type of the NamedBlobFile's `contentType` attribute (unicode -> str)

    ftw.mail's `createMailInContainer` function previously set it to unicode,
    but it should be string.
    """

    def __call__(self):
        for obj in self.objects({'portal_type': 'ftw.mail.mail'},
                                'Fix message.contentType (unicode -> str)'):
            message = obj.message
            if isinstance(message.contentType, unicode):
                message.contentType = message.contentType.encode('ascii')
