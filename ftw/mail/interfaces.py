from zope.interface import Interface
from zope import schema


class IMailInbound(Interface):
    """ Inbound Mail processor
    """
    
    def msg():
        """ Returns an email.Message instance of the mail that was sent
            to the inbound mail processor.
        """
        
    def sender():
        """ Returns the senders email address who sent the mail to the
            inbound mail processor.
        """
    def recipient():
        """ get the email address of the recipient
        """


class IDestinationResolver(Interface):
    """ A destination resolver provides a container object where
        mails can be stored.
    """

    def uuid():
        """Extract the uuid from recipient
        """

    def destination():
        """ Returns a container for storing incoming mails.
        """

    def email():
        """ Returns the email address of the current folder
        """


class IMailSettings(Interface):

    validate_sender = schema.Bool(
        title = u'Validate Sender',
        default = True,
        description = u'If enabled, inbound mails are only accepted if a '\
                      'user account with the senders email address exists.'
    )

    unwrap_mail = schema.Bool(
        title = u'Unwrap Forwarded Mails',
        default = True,
        description = u'If enabled, mails containing an attached mail are '\
                      'unwrapped and only the attached mail is stored.'
    )

    mail_domain = schema.TextLine(
        title=u"Mail domain",
        description=u'Enter the mail domain which will be used \
for sending mails into this site.',
        default=u'example.org')
