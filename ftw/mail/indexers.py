from ftw.mail.mail import IMail
from ftw.mail.utils import get_date_header
from plone.indexer.decorator import indexer
from DateTime import DateTime


@indexer(IMail)
def Date(object_, **kw):
    """indexes the date of emails"""
    email_date = object_.get_header("Date", True) or object_.created()
    return email_date
