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


class IEmailAddress(Interface):
    """ Returns the email address for an object or the object an email
    email address
    """

    def get_object_for_email(email):
        """ Extract the important data of an email address and returns the
            object
        """

    def get_email_for_object(obj, domain):
        """ Returns the generated email address for an object
        """


class IMailSettings(Interface):

    unwrap_mail = schema.Bool(
        title=u'Unwrap Forwarded Mails',
        default=True,
        description=u'If enabled, mails containing an attached mail are '
                    u'unwrapped and only the attached mail is stored.'
    )

    mail_domain = schema.TextLine(
        title=u"Mail domain",
        description=u'Enter the mail domain which will be used \
for sending mails into this site.',
        default=u'example.org')
