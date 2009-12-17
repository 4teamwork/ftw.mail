
# mail messages may contain alternative representations of a message.
# the following list defines the order which alternative is chosen.
PREFERRED_MULTIPART_ALTERNATIVES = [
    'multipart/mixed', 
    'multipart/digest',
    'multipart/related',
    'text/html',
    'text/plain',
]

EXIT_CODES = {
    'NOINPUT': 66,   # cannot open input
    'DATAERR': 65,   # data format error
    'NOUSER':  67,   # addressee unknown
    'CANTCREAT': 73, # can't create (user) output file
    'NOPERM': 77,    # permission denied 
}