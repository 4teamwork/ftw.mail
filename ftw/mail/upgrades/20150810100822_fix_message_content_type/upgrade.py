from ftw.upgrade import UpgradeStep
from ZODB.POSException import ConflictError
import logging

logger = logging.getLogger('ftw.upgrade')


class FixMessageContentType(UpgradeStep):
    """Fix type of the NamedBlobFile's `contentType` attribute (unicode -> str)

    ftw.mail's `createMailInContainer` function previously set it to unicode,
    but it should be string.
    """

    def __call__(self):
        for obj in self.objects({'portal_type': 'ftw.mail.mail'},
                                'Fix message.contentType (unicode -> str)'):

            # ftw.mail's cached `message` property behaves in weird ways
            # sometimes, that's why this upgrade step takes an unususally
            # defensive approach

            # initialize attributes (lazy attribute loading)
            obj.Title()

            message = obj.message
            try:
                if isinstance(message.contentType, unicode):
                    message.contentType = message.contentType.encode('ascii')
            except ConflictError:
                raise
            except Exception, e:
                logger.warn("Updating object {0} failed: {1}".format(
                    obj.absolute_url(), str(e)))
