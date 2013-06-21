from ftw.mail.interfaces import IEmailAddress
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.folderfactories import _allowedTypes
from zope.component import getMultiAdapter


class MailIn(ViewletBase):

    index = ViewPageTemplateFile('mail_templates/mail_in.pt')

    def available(self):
        """Only show viewlet if ftw.mail.mail is addable in current context
        """
        factories_view = getMultiAdapter((self.context, self.request),
                                         name='folder_factories')

        addContext = factories_view.add_context()
        allowed = _allowedTypes(self.request, addContext)

        return 'ftw.mail.mail' in [type_.id for type_ in allowed]

    def email(self):
        email = IEmailAddress(self.request)
        return email.get_email_for_object(self.context)
