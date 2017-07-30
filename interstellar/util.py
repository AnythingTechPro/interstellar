import os
import random
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer

FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

def load_font(filepath, private=True, enumerable=False):
    '''
    Makes fonts located in file `filepath` available to the font system.

    `private`     if True, other processes cannot see this font, and this
                  font will be unloaded when the process dies
    `enumerable`  if True, this font will appear when enumerating fonts

    See https://msdn.microsoft.com/en-us/library/dd183327(VS.85).aspx
    '''

    if not os.path.exists(filepath):
        raise IOError('Failed to find font file %s!' % filepath)

    # This function was taken from
    # https://github.com/ifwe/digsby/blob/f5fe00244744aa131e07f09348d10563f3d8fa99/digsby/src/gui/native/win/winfonts.py#L15
    # This function is written for Python 2.x. For 3.x, you
    # have to convert the isinstance checks to bytes and str
    if isinstance(filepath, str):
        pathbuf = create_string_buffer(filepath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExA
    elif isinstance(filepath, unicode):
        pathbuf = create_unicode_buffer(filepath)
        AddFontResourceEx = windll.gdi32.AddFontResourceExW
    else:
        raise TypeError('filepath must be of type str or unicode')

    flags = (FR_PRIVATE if private else 0) | (FR_NOT_ENUM if not enumerable else 0)
    numFontsAdded = AddFontResourceEx(byref(pathbuf), flags, 0)
    return bool(numFontsAdded)

def weighted_choice(choices):
    """
    Chooses a random item from the list based on probability
    """

    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c

        upto += w

    return None
