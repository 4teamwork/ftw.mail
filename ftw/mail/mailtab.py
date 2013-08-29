from DateTime import DateTime
from ftw.mail import _
from ftw.tabbedview.browser import listing
from ftw.table import helper
from ftw.table.helper import readable_author
from zope.i18n import translate


def get_mail_header(field=None, isdate=False):

    def _helper(item, value):
        if field is None:
            return ''

        obj = item.getObject()
        view = obj.restrictedTraverse('@@view')

        if isdate:
            date = DateTime(view.get_header(field))
            return helper.readable_date_time_text(item, date)

        elif field == 'attachments':
            imgpath = '++resource++attachment.png'
            return '<img src="%s" alt="%s" /> %s' % (
                imgpath,
                translate(_(u'attachment_icon_alt_text',
                           default=u'Attachment'),
                          context=obj.REQUEST),
                len(view.attachments()))

        else:
            return view.get_header(field)

    return _helper


class MailsTab(listing.CatalogListingView):
    """Lists all mails
    """

    types = ('ftw.mail.mail',)

    sort_on = 'modified'

    show_selects = False
    show_menu = False

    columns = (
        {'column': 'Title',
         'sort_index': 'sortable_title',
         'column_title': _(u'label_mailtab_subject',
                           default=u'Subject'),
         'transform': helper.linked},

        {'column': 'From',
         'column_title': _(u'label_mailstab_from',
                           default=u'From'),
         'transform': get_mail_header(field='From'),
         'sortable': False},

        {'column': 'To',
         'column_title': _(u'label_mailstab_to',
                           default=u'To'),
         'transform': get_mail_header(field='To'),
         'sortable': False},

        {'column': 'Date',
         'column_title': _(u'label_mailstab_date',
                           default=u'Date Received'),
         'transform': get_mail_header(field='Date', isdate=True),
         'sortable': False},

        {'column': 'Attachments',
         'column_title': _(u'label_mailstab_attachments',
                           default=u'Attachments'),
         'transform': get_mail_header(field='attachments'),
         'sortable': False},

        {'column': 'Creator',
         'column_title': _(u'label_mailstab_creator',
                           default=u'Creator'),
         'transform': readable_author},
        )
