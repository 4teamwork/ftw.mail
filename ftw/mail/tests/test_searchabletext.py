# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.testing import FTW_MAIL_FUNCTIONAL_TESTING
from unittest2 import TestCase
from unittest2 import skipUnless
import os


def asset(filename):
    here = os.path.dirname(__file__)
    path = os.path.join(here, 'mails', filename)
    with open(path, 'r') as file_:
        return file_.read()


def catalog_indexdata_of(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    path = '/'.join(obj.getPhysicalPath())
    return catalog.getIndexDataForUID(path)


class TestSearchableText(TestCase):

    layer = FTW_MAIL_FUNCTIONAL_TESTING

    def test_plain_text_body(self):
        mail = create(Builder('mail')
                      .with_message(asset('latin1.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('tyrannen', searchable_text)

    def test_utf8_encoded_body(self):
        mail = create(Builder('mail')
                      .with_message(asset('utf8.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('tyrannen', searchable_text)

    @skipUnless(getFSVersionTuple() < (4, 3), "Plone < 4.3")
    def test_umlauts_Plone_4_2_and_older(self):
        # The text contains the umlauts "äöu", which is indexed
        # as umlauts in Plone < 4.3
        mail = create(Builder('mail')
                      .with_message(asset('attachment.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('äöü', searchable_text)

    @skipUnless(getFSVersionTuple() >= (4, 3), "Plone >= 4.3")
    def test_umlauts_Plone_4_3_and_newer(self):
        # The text contains the umlauts "äöu", which is indexed
        # without diacritics (as "aou")  in Plone >= 4.3
        mail = create(Builder('mail')
                      .with_message(asset('attachment.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('aou', searchable_text)

    def test_attached_email(self):
        mail = create(Builder('mail')
                      .with_message(asset('fwd_attachment.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('consectetuer', searchable_text)

    def test_nested_attached_html_file(self):
        mail = create(Builder('mail')
                      .with_message(asset('nested_html_attachment.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertIn('consectetuer', searchable_text)

    def test_html_tags_are_not_indexed___converted(self):
        mail = create(Builder('mail')
                      .with_message(asset('latin1.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertNotIn('div', searchable_text)

    def test_html_tags_are_not_indexed(self):
        mail = create(Builder('mail')
                      .with_message(asset('fwd_attachment.txt')))
        searchable_text = catalog_indexdata_of(mail)['SearchableText']
        self.assertNotIn('div', searchable_text)
