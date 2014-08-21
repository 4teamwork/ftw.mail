from ftw.upgrade import UpgradeStep


class ReindexSearchableText(UpgradeStep):

    def __call__(self):
        self.catalog_reindex_objects({'portal_type': 'ftw.mail.mail'},
                                     idxs=['SearchableText'])
