from .report import *
from .genre import *
from .push import *
from .attachment import *
from .faq import *
from .wiki import *
from .subscription import *
from .tag import *

from emoji_picker.widgets import EmojiPickerTextInput, EmojiPickerTextarea

EmojiPickerTextInput.Media.js = ('admin/js/jquery.init.js', ) + EmojiPickerTextInput.Media.js
EmojiPickerTextarea.Media.js = ('admin/js/jquery.init.js', ) + EmojiPickerTextarea.Media.js
