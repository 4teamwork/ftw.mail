from zope.interface import Interface

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
