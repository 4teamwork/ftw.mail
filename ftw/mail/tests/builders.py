from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from plone.namedfile import NamedBlobFile


class MailBuilder(DexterityBuilder):
    portal_type = 'ftw.mail.mail'

    def with_message(self, data, contentType=u'message/rfc822', filename=u'message.eml'):
        self.arguments["message"] = NamedBlobFile(
            data=data, contentType=contentType, filename=filename)
        return self


builder_registry.register('mail', MailBuilder)
