from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from ftw.workspace.interfaces import IWorkspaceLayer
from plone.registry.interfaces import IRegistry
from unittest2 import TestCase
from zope.component import getUtility
from zope.interface import alsoProvides
import json
import os.path


def mail_asset(name, ext='txt'):
    tests_dir_path = os.path.dirname(__file__)
    filename = '.'.join((name, ext))
    return open(os.path.join(tests_dir_path, 'mails', filename))


class TestMailTab(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestMailTab, self).setUp()

        self.portal = self.layer.get('portal')

    def test_mail_tab_available(self):
        alsoProvides(self.portal.REQUEST, IWorkspaceLayer)
        view = self.portal.restrictedTraverse('tabbedview_view-mails')

        self.assertTrue(view, 'Mail tab is not available')

    def test_mail_date_parsing(self):
        create(Builder('mail').with_message(mail_asset('latin1')))
        mail_row = self.get_mails_tab_data().get('rows')[0]
        self.assertEquals('01.01.1970 01:00', mail_row.get('Date'))

    def test_mail_invalid_date_results_in_empty_string(self):
        create(Builder('mail').with_message(mail_asset('invalid_date')))
        mail_row = self.get_mails_tab_data().get('rows')[0]
        self.assertEquals('', mail_row.get('Date'))

    def test_mail_date_parsing_with_time_zone(self):
        create(Builder('mail').with_message(mail_asset('time_zone_dates')))
        mail_row = self.get_mails_tab_data().get('rows')[0]
        self.assertEquals('28.08.2010 18:50', mail_row.get('Date'))

    def get_mails_tab_data(self):
        request = self.portal.REQUEST
        alsoProvides(request, IWorkspaceLayer)
        registry = getUtility(IRegistry)
        registry['ftw.tabbedview.interfaces.ITabbedView.extjs_enabled'] = True
        request.form['tableType'] = 'extjs'
        view = self.portal.restrictedTraverse('tabbedview_view-mails')
        return json.loads(view())
