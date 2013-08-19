from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from ftw.workspace.interfaces import IWorkspaceLayer
from unittest2 import TestCase
from zope.interface import alsoProvides


class TestMailTab(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestMailTab, self).setUp()

        self.portal = self.layer.get('portal')

    def test_mail_tab_available(self):
        alsoProvides(self.portal.REQUEST, IWorkspaceLayer)
        view = self.portal.restrictedTraverse('tabbedview_view-mails')

        self.assertTrue(view, 'Mail tab is not available')


class TestNoMailTab(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestNoMailTab, self).setUp()

        self.portal = self.layer.get('portal')

    def test_mail_tab_is_not_available(self):

        self.assertRaises(KeyError,
            self.portal.restrictedTraverse, 'tabbedview_view-mails')
