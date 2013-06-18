from ftw.mail import _
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.i18n import translate
from ftw.mail.interfaces import IMailSettings
from plone.uuid.interfaces import IUUID


class MailIn(BrowserView):

    template = ViewPageTemplateFile('mail_templates/mail_in.pt')

    def __call__(self):
        return self.template()

    def title(self):
        return translate(_(u'Mail in of ${title}',
                           mapping={'title': self.context.Title()}),
                           context=self.request)

    def email(self):
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IMailSettings)
        domain = getattr(proxy, 'mail_domain', 'nodomain.com')
        return '%s@%s' % (IUUID(self.context), domain)
