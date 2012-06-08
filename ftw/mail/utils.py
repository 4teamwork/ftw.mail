# various utility methods for handling e-mail messages
from email.header import decode_header
from email.Utils import mktime_tz, parsedate_tz
from DocumentTemplate.DT_Util import html_quote
from BeautifulSoup import BeautifulSoup
import re
from ftw.mail import config

# a regular expression that matches src attributes of img tags containing a cid
IMG_SRC_RE = re.compile(r'<img[^>]*?src="cid:([^"]*)', re.IGNORECASE|re.DOTALL)
BODY_RE = re.compile(r'<body>(.*)</body>', re.IGNORECASE|re.DOTALL)

def safe_decode_header(value):
    """ Handles rfc 2047 encoded header with non-ascii characters.
    Always returns an utf-8 encoded string.
    """

    if value is None:
        return None

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    new_value = []

    for data, charset in decode_header(value):
        if charset is not None and charset not in ('utf-8', 'utf8'):
            data = data.decode(charset).encode('utf-8')
        elif charset is None:
            data = safe_utf8(data)
        new_value.append(data and data or '')

    return ' '.join(new_value).rstrip()


def get_header(msg, name):
    """Returns the value of the named header field of a mail message.
    Handles rfc 2047 encoded header with non-ascii characters.
    Always returns an utf-8 encoded string.
    """
    value = ''
    if msg is not None and msg.has_key(name):
        value = safe_decode_header(msg.get(name))
    return value

def get_date_header(msg, name):
    """ Returns an UTC timestamp from a header field containing a date.
    Compensates for the timezone difference if the header contains
    timezone information.
    """
    value = get_header(msg, name)
    ts = 0.0
    try:
        ts = mktime_tz(parsedate_tz(value))
    except TypeError:
        pass
    return ts

def get_payload(msg):
    """Get the decoded message payload as utf-8 string"""

    # get encoding for the msg object, use utf-8 as fallback encoding
    # for msg objects without a correct charset information
    encoding = msg.get_content_charset('utf-8')
    payload = msg.get_payload(decode=1)
    try:
        payload = payload.decode(encoding)
    except UnicodeDecodeError:
        payload = payload.decode('iso-8859-1', 'replace')
    payload = payload.encode('utf-8')
    return payload

def get_body(msg, url_prefix=''):
    """Returns the mail body as HTML string. All text parts of a multipart
    message are returned."""
    html = ''
    parts = get_text_payloads(msg)
    for part in parts:
        html += part
    html = adjust_image_tags(html, msg, url_prefix)
    return html

def get_attachments(msg):
    """ Returns a list describing the attachements. Only attachments with
    a filename are returned."""
    attachments = []
    if msg is not None and msg.is_multipart():
        for position,part in enumerate(msg.walk()):
            content_type = part.get_content_type()
            filename = get_filename(part)
            if filename is None:
                continue
            # determine size
            size = 0
            if content_type == 'message/rfc822':
                size = len(part.as_string())
            else:
                size = len(part.get_payload(decode=1))
            attachments.append({'filename': filename,
                                'content-type': content_type,
                                'size': size,
                                'position': position})
    return attachments

def remove_attachments(msg, positions):
    """Remove all attachments which have position listed in `positions`
    from the email Message `msg`.
    Returns the same email Message object without attachments.
    If `clone` is True, the message will be copied first
    """

    if msg is None:
        raise ValueError('Cannot delete attachments from email message None')

    if 0 in positions:
        raise ValueError('Cannot delete the message itself (position 0)')

    if len(positions) == 0:
        # no attachments should be removed - so just skip
        return msg

    if not msg.is_multipart():
        raise ValueError('Email message is not multipart - there are '
                         'no attachments.')

    # get the parts to delete filtering the position
    parts_to_delete = [part for pos, part in enumerate(msg.walk())
                           if pos in positions]

    if len(positions) != len(parts_to_delete):
        raise ValueError('One or more attachments could not be found.')

    def _recursive_remove_parts(msg):
        """Recursive function for removing payloads (attachments).
        """
        if not msg.is_multipart():
            return msg

        new_payload = []
        for part in msg.get_payload():
            if part not in parts_to_delete:
                new_payload.append(_recursive_remove_parts(part))
        msg.set_payload(new_payload)
        return msg

    # do it
    return _recursive_remove_parts(msg)

def get_text_payloads(msg):
    """Go recursivly through the message parts and return a list of all
    text parts in HTML format"""
    if msg is None:
        return []
    parts = []
    if msg.is_multipart():
        msgs = msg.get_payload()
        # we only want the best alternative
        if msg.get_content_type() == 'multipart/alternative':
            alternatives = []
            for part in msgs:
                alternatives.append(part.get_content_type())
            best_pos = get_best_alternative(alternatives)
            parts += get_text_payloads(msgs[best_pos])
        # we go through all parts
        else:
            for part in msgs:
                parts += get_text_payloads(part)
    # not a multipart message
    else:
        payload = get_payload(msg)
        if payload:
            if msg.get_content_type() == 'text/html':
                parts.append(payload)
            elif msg.get_content_type() == 'text/plain':
                parts.append(text2html(payload))
    return parts

def adjust_image_tags(html, msg, url_prefix):
    """Adjust image tags of the given HTML string which reference an image by
    Content-Id. The src attribute is set to the attachment of the given message."""

    matches = IMG_SRC_RE.findall(html)
    for m in matches:
        pos = get_position_for_cid(msg, m)
        html = html.replace('cid:' + m, '%s/get_attachment?position=%s' % (url_prefix, pos))
    return html

def get_position_for_cid(msg, cid):
    """Return the position of the message part with the given Content-Id"""
    position = -1
    cid = '<' + cid + '>'
    for part in msg.walk():
        position += 1
        if part.get('Content-Id', None) == cid:
            return position
        return position

def get_filename(msg):
    """Get the filename of a message (part)
    """
    filename = msg.get_filename(None)

    if filename is None:
        filename = msg.get_param('Name', None)

    # if the value is already decoded or another tuple
    # we just take the value and use the decode_header function
    if isinstance(filename, tuple):
        if filename[0] is not None and filename[0] not in ('utf-8', 'utf8'):
            filename = filename[2].decode(filename[0]).encode('utf-8')
        else:
            filename = safe_utf8(filename[2])

    else:
        filename = safe_decode_header(filename)

    return filename

def get_best_alternative(alternatives):
    """Get the index of the most preferred alternative in the given list of
    alternatives.
    """
    for content_type in config.PREFERRED_MULTIPART_ALTERNATIVES:
        if content_type in alternatives:
            return alternatives.index(content_type)
    return 0

def text2html(text):
    """Replaces all line breaks with a br tag, and wraps it in a p tag.
    """
    return '<p>%s</p>' % html_quote(text.strip()).replace('\n', '<br />')

def unwrap_html_body(html, css_class=None):
    """ Return the content of the body tag for inline display in another
    html document.
    """
    soup = BeautifulSoup(html, fromEncoding='utf8')
    if soup.body:
        soup = soup.body
    body_soup = BeautifulSoup('<div>%s</div>' % soup.renderContents(), fromEncoding='utf8')
    if css_class:
        body_soup.div['class'] = css_class
    body_style = soup.get('style')
    if body_style:
        body_soup.div['style'] = body_style
    return body_soup.renderContents()

def unwrap_attached_msg(msg):
    """ If a msg contains an attachmed message return the attached one.
    """
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'message/rfc822':
                return part.get_payload(0)
    return msg

def safe_utf8(text):
    """Returns an utf-8 encoded version of the given string with unknown
    encoding.
    """
    encodings = ('utf8', 'iso-8859-1', 'iso-8859-15')
    for enc in encodings:
        try:
            text = text.decode(enc)
            return text.encode('utf8')
        except UnicodeDecodeError:
            pass
    return text.decode('ascii', 'replace').encode('utf8')
