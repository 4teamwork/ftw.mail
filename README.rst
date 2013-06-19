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

The major feature of ``ftw.mail`` is the mail inbound.
Mail inbound allows you to send emails directly to your Plone site.
An email sent to Plone will be extracted and created as mail contenttype
automatically.

**Security**

1. There must be a registered user with the sender email address
2. The user must have enough permissions to add a mail object in the folder
3. The email will be created with the security context of the sender

**What is the email address?**

The default implementation is using the objects uuid.
Simply call `mail-in` on a folder, the view will show you the email address.
The domain can be configured in the plone registry.


Installing
==========

- Add ``ftw.mail`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.mail

- Install the generic import profile.


**Enable Mail-Inbound Feature**

Install the [mta2plone.py](https://github.com/4teamwork/ftw.mail/blob/master/ftw/mail/mta2plone.py)
script somewhere in the PATH of your server.
Be sure mta2plone.py is executable (`chmod +x mta2plone.py`).

Example Postfix configuration in `/etc/postfix/virtual`::

    inbound.example.org anything
    @inbound.example.org inbound-example


Example `/etc/aliases`::

    inbound-example: "|/path/to/mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound"


For local testing it is also possible to start the `mta2plone.py`
in a console and paste the raw mail to `stdin`:

.. code:: bash

    ./mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound recipient-email


THIS NEEDS MORE DOCUMENTATION



Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.1`, `4.2` or `4.3`.


Links
=====

- Main github project repository: https://github.com/4teamwork/ftw.mail
- Issue tracker: https://github.com/4teamwork/ftw.mail/issues
- Package on pypi: http://pypi.python.org/pypi/ftw.mail
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.mail


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.mail`` is licensed under GNU General Public License, version 2.
