from ftw.mail.mail import IMail
from plone.indexer.decorator import indexer


@indexer(IMail)
def Date(object_, **kw):
    """indexes the date of emails"""
    email_date = object_.get_header("Date", True) or object_.created()
    return email_date
