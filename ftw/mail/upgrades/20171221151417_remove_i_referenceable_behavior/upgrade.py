from ftw.upgrade import UpgradeStep


class RemoveIReferenceableBehavior(UpgradeStep):
    """Remove IReferenceable behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
