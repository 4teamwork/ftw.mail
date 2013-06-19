from ftw.mail import _
from ftw.mail.interfaces import IDestinationResolver
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate


class MailIn(BrowserView):

    template = ViewPageTemplateFile('mail_templates/mail_in.pt')

    def __call__(self):
        return self.template()

    def title(self):
        return translate(_(u'Mail in of ${title}',
                           mapping={'title': self.context.Title()}),
                           context=self.request)

    def email(self):
        resolver = IDestinationResolver(self.context)
        return resolver.email
