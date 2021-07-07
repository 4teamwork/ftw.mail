from ftw.upgrade import UpgradeStep


class RebuildMailCacheForSignedMultipart(UpgradeStep):
    """Rebuild mail attachment info cache for signed/multipart.
    """

    deferrable = True

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}
        for mail in self.objects(query, 'Rebuild signed/multipart attachment'):
            self.maybe_rebuild_attachment_infos(mail)

    def maybe_rebuild_attachment_infos(self, mail):
        for info in mail.attachment_infos:
            if info.get('content-type') == 'multipart/signed':
                # In the future it should be avoided to overwrite the permanent
                # attachment info cache. Gever uses it to store additional data.
                mail._update_attachment_infos()
                return
