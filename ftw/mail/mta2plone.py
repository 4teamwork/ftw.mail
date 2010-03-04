#!/usr/bin/python

import sys, urllib


def post_message(url, recipient, message_txt):
    """ post an email message to the given url
    """

    if not url:
        print "Invalid url."
        print "usage: mta2plone.py url <recipient>"
        sys.exit(64)

    data = {'mail': message_txt}
    if len(recipient) > 0:
        data ['recipient'] = recipient
        
    try:
        result = urllib.urlopen(url, urllib.urlencode(data)).read()
    except (IOError,EOFError),e:
        print "ftw.mail error: could not connect to server",e
        sys.exit(73)

    try:
        exitcode, errormsg = result.split(':')
        if exitcode != '0':
            print 'Error %s: %s' % (exitcode, errormsg)
            sys.exit(int(exitcode))
    except ValueError:
        print 'Unknown error.'
        sys.exit(69)

    sys.exit(0)


if __name__ == '__main__':
    # This gets called by the MTA when a new message arrives.
    # The mail message file gets passed in on the stdin
        
    # Get the raw mail
    message_txt = sys.stdin.read()
        
    url = ''
    if len(sys.argv)>1:
        url = sys.argv[1]
        
    recipient = ''
    if len(sys.argv)>2:
        recipient = sys.argv[2]

    post_message(url, recipient, message_txt)
