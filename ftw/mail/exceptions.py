from ftw.mail.config import EXIT_CODES


class MailInboundException(Exception):
    """ An exception indicating an error occured while processing
        an inbound mail.
    """
    def __init__(self, exitcode, errormsg):
        self.exitcode = exitcode
        self.errormsg = errormsg

    def __str__(self):
        return '%s:%s' % (self.exitcode, self.errormsg)


class NoInput(MailInboundException):

    def __init__(self):
        MailInboundException.__init__(
            self, EXIT_CODES['NOINPUT'], 'No mail message supplied.')


class InvalidMessage(MailInboundException):

    def __init__(self):
        MailInboundException.__init__(
            self, EXIT_CODES['DATAERR'], 'Invalid mail message supplied.')


class NoSenderFound(MailInboundException):

    def __init__(self, mail):
        self.mail = mail
        MailInboundException.__init__(
            self, EXIT_CODES['NOPERM'], 'Could not extract sender email.')


class UnknownSender(MailInboundException):

    def __init__(self, mail):
        self.mail = mail
        MailInboundException.__init__(
            self, EXIT_CODES['NOPERM'], 'Unknown sender. Permission denied.')


class PermissionDenied(MailInboundException):

    def __init__(self, mail, user):
        self.mail = mail
        self.user = user
        MailInboundException.__init__(
            self, EXIT_CODES['NOPERM'],
            'Unable to create message. Permission denied.')


class DisallowedSubobjectType(MailInboundException):

    def __init__(self, mail, user):
        self.mail = mail
        self.user = user
        MailInboundException.__init__(
            self, EXIT_CODES['NOPERM'],
            'Disallowed subobject type. Permission denied.')


class DestinationDoesNotExist(MailInboundException):

    def __init__(self, emailaddress):
        self.emailaddress = emailaddress
        MailInboundException.__init__(
            self, EXIT_CODES['CANTCREAT'],
            'Destination does not exist.')
