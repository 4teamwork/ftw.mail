from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.mail.interfaces import IEmailAddress
from plone.app.content.browser.folderfactories import _allowedTypes
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter


class MailIn(ViewletBase):

    index = ViewPageTemplateFile('mail_templates/mail_in.pt')

    def available(self):
        """Only show viewlet if ftw.mail.mail is addable in current context
        """

        portal_types = getToolByName(self.context, 'portal_types')
        fti = portal_types.get(self.context.portal_type)
        return 'ftw.mail.mail' in fti.allowed_content_types

    def email(self):
        email = IEmailAddress(self.request)
        return email.get_email_for_object(self.context)
