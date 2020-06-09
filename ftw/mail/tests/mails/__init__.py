from pkg_resources import resource_string
import email


def load(filename):
    return resource_string('ftw.mail.tests.mails', filename)


def load_mail(filename):
    return email.message_from_string(load(filename))
