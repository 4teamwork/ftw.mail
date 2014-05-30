from ftw.upgrade import UpgradeStep


class UpdatePersistentCaches(UpgradeStep):

    def __call__(self):
        query = {'object_provides': ['ftw.mail.mail.IMail']}
        for mail in self.objects(query, 'Update mail caches'):
            # reset the message to trigger updating of all caches
            mail.Title()  # Fucking caches.
            mail.message = vars(mail).get('message')
