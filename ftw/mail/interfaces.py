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
    def destination():
        """ Returns a container for storing incoming mails.
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
