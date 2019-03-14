Introduction
============

``ftw.mail`` provides a dexterity based mail contenttype which allows you to
upload emails to your Plone site.
This includes extracting of important data of the email, like:

- Attachments
- Mail header
- Body text
- Unwrap attached emails (msg).


Mail-Inbound functionality
==========================

The major feature of ``ftw.mail`` is the inbound mail functionality.
Mail inbound allows you to send emails directly to your Plone site.
An email sent to Plone will be extracted and created as mail contenttype
automatically.

**Security**

1. There must be a registered user with the sender email address
2. The user must have enough permissions to add a mail object in the folder
3. The email will be created with the security context of the sender

**What is the email address?**

The localpart of the email address is a unique identifier that
identifies the respective folderish object. The default implementations
uses the object's UUID. The mail-in address will automatically shown in a
viewlet if `ftw.mail.mail` content type is addable.


Installing
==========

- Add ``ftw.mail`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.mail

- Install the generic setup import profile.


**Enable Mail-Inbound Feature**

Install the `mta2plone.py <https://github.com/4teamwork/ftw.mail/blob/master/ftw/mail/mta2plone.py>`_
script somewhere in the PATH of your server.
Make sure mta2plone.py is executable (`chmod +x mta2plone.py`).

Example Postfix configuration in `/etc/postfix/virtual`::

    inbound.example.org anything
    @inbound.example.org inbound-example


Example `/etc/aliases`::

    inbound-example: "|/path/to/mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound"


Remember to run the ``newaliases`` command (as root) after you update /etc/aliases in order for Postfix to pick up the changes.


For local testing it is also possible to start the `mta2plone.py`
in a console and paste the raw mail to `STDIN`:

.. code:: bash

    ./mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound recipient-email

(Since the `mta2plone.py` script will read from STDIN, you'll need to send an EOF using CTRL-D after you pases the mail contents.)


Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.3`.


Links
=====

- Github: https://github.com/4teamwork/ftw.mail
- Issues: https://github.com/4teamwork/ftw.mail/issues
- Pypi: http://pypi.python.org/pypi/ftw.mail
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.mail


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.mail`` is licensed under GNU General Public License, version 2.
