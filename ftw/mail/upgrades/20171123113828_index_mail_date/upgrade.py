from ftw.upgrade import UpgradeStep


class IndexMailDate(UpgradeStep):
    """Update Date field in mail cache to new format
    and index mail date in the Date index field
    """

    def __call__(self):
        query = {'portal_type': 'ftw.mail.mail'}
        msg = 'Update E-mail cache.'
        for mail in self.objects(query, msg):
            if hasattr(mail, "_header_cache") and "Date" in mail._header_cache:
                del mail._header_cache["Date"]
        self.catalog_reindex_objects(query, idxs=['Date'])
