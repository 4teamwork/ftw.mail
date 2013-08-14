from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles


class TestMailInViewlet(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer.get('portal')
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])

        self.portal.invokeFactory('Folder', 'f1')
        self.folder = self.portal['f1']

    def get_viewlet(self, context):
        view = BrowserView(context, context.REQUEST)
        manager_name = 'plone.belowcontenttitle'
        manager = queryMultiAdapter(
            (context, context.REQUEST, view),
            IViewletManager,
            manager_name)

        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'ftw.mail.mail-in'
        viewlets = [v for v in manager.viewlets if v.__name__ == name]

        if len(viewlets):
            return viewlets[0]
        else:
            return None

    def test_viewlet_registered(self):
        self.assertNotEquals(None, self.get_viewlet(self.folder),
            'The ftw.mail.mail-in viewlet is not registered properly')

    def test_viewlet_is_present_if_mail_is_addable(self):
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types.get('Folder').allowed_content_types = ['ftw.mail.mail']

        viewlet = self.get_viewlet(self.folder)

        self.assertTrue(viewlet.available(),
            'Expect the ftw.mail-mail-in viewlet on %s' % (
                self.folder.absolute_url()))

    def test_viewlet_is_not_present_if_mail_is_not_addable(self):
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types.get('Folder').allowed_content_types = []

        viewlet = self.get_viewlet(self.folder)

        self.assertFalse(viewlet.available(),
            'Did not expect the ftw.mail-mail-in viewlet on %s' % (
                self.folder.absolute_url()))

    def test_mailin_email(self):
        viewlet = self.get_viewlet(self.folder)
        expect = "%s@example.org" % IUUID(self.folder)

        self.assertEquals(expect, viewlet.email())
