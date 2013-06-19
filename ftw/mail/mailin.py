from ftw.mail import _
from ftw.mail.interfaces import IEmailAddress
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


class MailIn(BrowserView):

    template = ViewPageTemplateFile('mail_templates/mail_in.pt')

    def __call__(self):
        return self.template()

    def title(self):
        return translate(_(u'Mail-In of ${title}',
                           mapping={'title': self.context.Title()}),
                           context=self.request)

    def email(self):
        email = IEmailAddress(self.request)
        return email.get_email_for_object(self.context)
