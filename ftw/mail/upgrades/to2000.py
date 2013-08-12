from ftw.upgrade import UpgradeStep


class RevokeAddMailPermission(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.mail.upgrades:2000')
