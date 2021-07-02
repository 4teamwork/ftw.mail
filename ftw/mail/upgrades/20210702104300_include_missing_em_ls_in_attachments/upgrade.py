from ftw.mail import utils
from ftw.upgrade import UpgradeStep
import logging

LOG = logging.getLogger('ftw.upgrade')


class IncludeMissingEMLsInAttachments(UpgradeStep):
    """Include missing emls in attachments.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Include missing emls in attachments'):
            self.add_missing_eml_attachments(mail)

    def add_missing_eml_attachments(self, obj):
        attachments = utils.get_attachments(obj.msg)
        if len(attachments) == len(obj.attachment_infos):
            return

        info_list = list(obj.attachment_infos)
        stored_positions = [each['position'] for each in info_list]

        for attachment in attachments:
            if attachment['position'] in stored_positions:
                continue
            if (attachment['filename'] != "attachment.eml" or
                    attachment['content-type'] != "message/rfc822"):
                LOG.warning(u"Found missing attachment that is not in-line eml"
                            u"for {}. {}".format(obj.absolute_url(), attachment))
                continue
            info_list.append(attachment)
        obj._attachment_infos = tuple(sorted(info_list, key=lambda x: x["position"]))
