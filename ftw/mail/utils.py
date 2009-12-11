# various utility methods for handling e-mail messages
from email import Header
from DocumentTemplate.DT_Util import html_quote
import re
from ftw.mail import config

# a regular expression that matches src attributes of img tags containing a cid
IMG_SRC_RE = re.compile(r'<img[^>]*?src="cid:([^"]*)', re.IGNORECASE|re.DOTALL)

def get_header(msg, name):
    """Returns the value of the named header field of a mail message.
       Handles rfc 2047 encoded header with non-ascii characters.
       Always returns an utf-8 encoded string.
    """
    value = ''
    if msg is not None and msg.has_key(name):
        header = msg.get(name)
        decoded = Header.decode_header(header)
        for part in decoded:
            part_value = part[0]
            encoding = part[1]
            if encoding is not None and encoding != 'utf-8':
                part_value = part_value.decode(encoding).encode('utf8')
            value += part_value + ' '
    return value.rstrip()

def get_payload(msg):
    """Get the decoded message payload as utf-8 string"""
    encoding = msg.get_content_charset('ascii')
    payload = msg.get_payload(decode=1)
    try: 
        payload = payload.decode(encoding)
    except UnicodeDecodeError:
        payload = payload.decode('iso-8859-1', 'replace')
    payload = payload.encode('utf-8')
    return payload
    
def get_body_as_html(msg, url_prefix=''):
    """Returns the mail body as HTML string. All text parts of a multipart
       message are returned."""
    html = ''
    parts = get_text_payloads(msg)
    for part in parts:
        html += part
    html = adjust_image_tags(html, msg, url_prefix)
    return html

def get_text_payloads(msg):
    """Go recursivly through the message parts and return a list of all
    text parts in HTML format"""
    if msg is None:
        return ''
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
    elif msg.get_content_type() == 'text/html':
        parts.append(get_payload(msg))
    elif msg.get_content_type() == 'text/plain':
        parts.append(text2html(get_payload(msg))) 
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
    html_quote(text.strip()).replace('\n', '<br />')
