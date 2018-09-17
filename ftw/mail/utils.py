# various utility methods for handling e-mail messages
from BeautifulSoup import BeautifulSoup
from DocumentTemplate.DT_Util import html_quote
from email.header import decode_header
from email.Utils import mktime_tz, parsedate_tz
from ftw.mail import config
import re


# a regular expression that matches src attributes of img tags containing a cid
IMG_SRC_RE = re.compile(r'<img[^>]*?src="cid:([^"]*)', re.IGNORECASE | re.DOTALL)
BODY_RE = re.compile(r'<body>(.*)</body>', re.IGNORECASE | re.DOTALL)
APPLE_PARTIAL_ENCODING_RE = re.compile(r'^"(.*=\?.*\?=.*)"( <.*>)$')
ENCODED_WORD_WITHOUT_LWSP = re.compile(r'(=\?.*?\?=)(\r\n)([ \t])')
ENCODED_WORD_WITHOUT_NEWLINES = re.compile(r'(=\?.*?\?[BQ]\?.*?)([\r\n])(.*?\?=)')

# Used to fix broken meta tags that confuse TAL
# Largely copied from zope.pagetemplate.pagetemplatefile, adjusted for the
# missing semicolon between mimetype and charset declaration
broken_meta_pattern = re.compile(
    r'\s*<meta\s+http-equiv=["\']?Content-Type["\']?'
    r'\s+content=["\']?([^;]+)\s*charset=([^"\']+)["\']?\s*/?\s*>\s*',
    re.IGNORECASE)


def safe_decode_header(value):
    """Handles rfc 2047 encoded header with non-ascii characters.
    Always returns an utf-8 encoded string.
    """
    if value is None:
        return None

    if isinstance(value, unicode):
        value = value.encode('utf-8')

    new_value = []

    # When sending mails with Apple Mail, which have umlauts in
    # From-/To-/Cc-Headers, it encodes the name of the person but it
    # wraps it into quotes.
    # The python email module does not support this wrapping, so we
    # remove the quotes in this situation.
    # Example:
    # From: "=?iso-8859-1?Q?Boss_H=FCgo?=" <hugo@boss.com>
    apple_partial_encoding = APPLE_PARTIAL_ENCODING_RE.match(value)
    if apple_partial_encoding:
        value = ''.join(apple_partial_encoding.groups())

    # Fix up RFC 2047 encoded words separated by 'CRLF LWSP' (which is fine
    # according to the RFC) by replacing the CRLF with a SPACE so
    # decode_header can parse them correctly.
    # This works around a bug in decode_header that has been fixed in 3.3.
    # See http://bugs.python.org/issue4491 and its duplicate.
    # Example:
    # From: =?utf-8?Q?B=C3=A4rengraben?=\r\n <from@example.org>
    value = re.sub(ENCODED_WORD_WITHOUT_LWSP, '\\1 \\3', value)

    # Despite being allowed by RFC 1342, newlines inside encoded words will
    # break the python 2.7 decode_header.
    # https://github.com/python/cpython/blob/2.7/Lib/email/header.py#L78
    # This workaround removes newlines only from valid encoded words.
    value = re.sub(ENCODED_WORD_WITHOUT_NEWLINES, '\\1 \\3', value)

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
    if msg is not None and name in msg:
        value = safe_decode_header(msg.get(name))
    return value


def get_date_header(msg, name):
    """Returns an UTC timestamp from a header field containing a date.
    Compensates for the timezone difference if the header contains
    timezone information.
    """
    value = get_header(msg, name)
    ts = None
    try:
        ts = mktime_tz(parsedate_tz(value))
    except TypeError:
        pass
    return ts


def get_payload(msg):
    """Get the decoded message payload as utf-8 string."""
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
    message are returned.
    """
    result = []
    for part in get_text_payloads(msg):
        result.append(adjust_image_tags(part, msg, url_prefix))
    return result


def get_part_size(content_type, part):
    if content_type == 'message/rfc822':
        return len(part.as_string())

    payload = part.get_payload(decode=1) or part.get_payload()
    if isinstance(payload, str):
        return len(payload)

    if not payload:
        return 0

    return sum(get_part_size(content_type, part) for part in payload)


def parse_part(part):
    content_type = part.get_content_type()
    filename = get_filename(part)
    size = get_part_size(content_type, part)
    return content_type, filename, size


def get_attachments(msg):
    """Returns a list describing the attachements. Only attachments with
    a filename are returned.
    """
    attachments = []

    if msg is not None and msg.is_multipart():
        for position, part in enumerate(msg.walk()):
            content_type, filename, size = parse_part(part)

            if filename is None:
                continue

            attachments.append({
                'filename': filename,
                'content-type': content_type,
                'size': size,
                'position': position,
            })

    return attachments


def remove_attachments(msg, positions):
    """Remove all attachments which have position listed in `positions`
    from the email Message `msg`.

    Returns the same email Message object without attachments.
    If `clone` is True, the message will be copied first.
    """
    if msg is None:
        raise ValueError('Cannot delete attachments from email message None')

    if 0 in positions:
        raise ValueError('Cannot delete the message itself (position 0)')

    if not positions:
        # no attachments should be removed - so just skip
        return msg

    if not msg.is_multipart():
        raise ValueError('Email message is not multipart - there are '
                         'no attachments.')

    # get the parts to delete filtering the position
    parts_to_delete = [part for pos, part in enumerate(msg.walk()) if pos in positions]

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
    text parts in HTML format.
    """
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
    Content-Id. The src attribute is set to the attachment of the given
    message.

    """
    matches = IMG_SRC_RE.findall(html)
    for m in matches:
        pos = get_position_for_cid(msg, m)
        if pos:
            download_url = '%s/get_attachment?position=%s' % (url_prefix, pos)
            html = html.replace('cid:' + m, download_url)
    return html


def get_position_for_cid(msg, cid):
    """Return the position of the message part with the given Content-Id."""
    position = -1
    cid = '<' + cid + '>'
    for part in msg.walk():
        position += 1
        if part.get('Content-Id', None) == cid:
            return position
    return None


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
    """Return the content of the body tag for inline display in another
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


def fix_broken_meta_tags(html):
    """Fix broken <meta /> tags in HTML MIME parts.

    text/html MIME parts of a multipart message may include <meta /> tags that
    declare a charset that differs from the encoding that is used for the page
    template that part is inserted into.

    zope.pagetemplate attempts to handle meta tags when inserting markup
    with 'structure', by re-encoding the inserted markup and adjusting the
    rewriting the meta tag's charset.

    If however the <meta /> tag is broken and doesn't match zope.pt's regex,
    the re-encoding doesn't take place and TAL / zope.pt chokes on the
    resulting mojibake, omitting parts of the document.

    This addresses one specific case seen in the wild in a message created
    with Apple Mail (2.2104), where the semicolon (;) is missing between the
    MIME type and the charset declaration. Example:

    <meta http-equiv="Content-Type" content="text/html charset=us-ascii">
    """
    match = broken_meta_pattern.search(html)

    if match:
        mimetype, charset = [g.strip() for g in match.groups()]
        fixed_tag = '\n<meta http-equiv="Content-Type" '\
                    'content="%s; charset=%s">\n' % (mimetype, charset)
        return re.sub(broken_meta_pattern, fixed_tag, html)

    return html


def unwrap_attached_msg(msg):
    """If a msg contains an attachmed message return the attached one."""
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
