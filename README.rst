Introduction
============

``ftw.mail`` provides a dexterity based Mail contenttype which allows you to
upload Emails to your Plone site.
This includes extracting of important data of the Email, like:
- Attachments
- Mail header
- Body text
- Unwrap attached emails (msg).


Mail-Inbound functionality
==========================

The major feature of ``ftw.mail``is called "Mail-Inbound".
"Mail-Inbound" allows you to send emails directly to your plone site.
An Email sent to Plone will be extracted and created as Mail contenttype
automatically.

**About security**
1. There must be a registered user with the sender email address.
2. The user must have enough permissions to add a Mail in the specific
   context
3. The Email will be created with the security context of the sender.

**What Email address?**
The default implementation is using the objects uuid.
Simply call `mail-in` on a folder, the view will show you the email address.
The domain can be configured through the plone registry.


Installing
==========

- Add ``ftw.mail`` to your buildout configuration:

::

    [instance]
    eggs +=
        ftw.mail

- Install the generic import profile.


**Enable Mail-Inbound Feature**

Make mta2plone.py available (it's located in ftw.mail/ftw/mail)
Symlink or copy the file to /usr/local/bin, or wherever it makes sense to you :-)
Be sure mta2plone.py is executable (chmod +x).

Assume you have postfix

Postfix configuration /etc/postfix/virtual:
```
inbound.example.org anything
@inbound.example.org inbound-example
```

/etc/aliases
```
inbound-example: "|/path/to/mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound"
```


For local testing it's also possible to start the mta2plone.py manually
in a console and paste the raw Mail to stdin.

```
./mta2plone.py http://127.0.0.1:8080/Plone/mail-inbound recipient-email
```



THIS NEEDS MORE DOCUMENTATION



Compatibility
-------------

Runs with `Plone <http://www.plone.org/>`_ `4.0`, `4.1`, `4.2` or `4.3`.


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

.. image:: https://cruel-carlota.pagodabox.com/d3e4ca26391a0beac20e5c8ff77e5559
   :alt: githalytics.com
   :target: http://githalytics.com/4teamwork/ftw.mail
