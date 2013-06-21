from ftw.mail.tests.layer import Layer
from plone.uuid.interfaces import IUUID
from Products.PloneTestCase.ptc import PloneTestCase
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from zope.viewlet.interfaces import IViewletManager
from Products.CMFCore.utils import getToolByName


class TestMailInViewlet(PloneTestCase):

    layer = Layer

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
        self.assertIsNotNone(self.get_viewlet(self.folder),
            'The ftw.mail.mail-in viewlet is not registered properly')

    def test_viewlet_is_present_if_mail_is_addable(self):
        viewlet = self.get_viewlet(self.folder)

        self.assertTrue(viewlet.available(),
            'Expect the ftw.mail-mail-in viewlet on %s' % (
                self.folder.absolute_url()))

    def test_viewlet_is_not_present_if_mail_is_not_addable(self):
        portal_types = getToolByName(self.portal, 'portal_types')
        portal_types.get('ftw.mail.mail').global_allow = False

        viewlet = self.get_viewlet(self.folder)

        self.assertFalse(viewlet.available(),
            'Did not expect the ftw.mail-mail-in viewlet on %s' % (
                self.folder.absolute_url()))

    def test_mailin_email(self):
        viewlet = self.get_viewlet(self.folder)
        expect = "%s@example.org" % IUUID(self.folder)

        self.assertEquals(expect, viewlet.email())
