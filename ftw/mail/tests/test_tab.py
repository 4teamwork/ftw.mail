from ftw.mail.tests.layer import Layer
from ftw.mail.tests.layer import WorkspaceLayer
from Products.PloneTestCase.ptc import PloneTestCase
from zope.interface import alsoProvides
from ftw.workspace.interfaces import IWorkspaceLayer


class TestMailTab(PloneTestCase):

    layer = WorkspaceLayer

    def test_mail_tab_available(self):
        alsoProvides(self.portal.REQUEST, IWorkspaceLayer)
        view = self.portal.restrictedTraverse('tabbedview_view-mails')

        self.assertTrue(view, 'Mail tab is not available')


class TestNoMailTab(PloneTestCase):

    layer = Layer

    def test_mail_tab_is_not_available(self):

        self.assertRaises(KeyError,
            self.portal.restrictedTraverse, 'tabbedview_view-mails')
