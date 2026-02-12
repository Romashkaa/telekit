# Copyright (c) 2025 Romashka
# Licensed under the MIT License.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ._handler import Handler
from ._chain import Chain
from ._callback_query_handler import CallbackQueryHandler
from .server import Server, example
from ._snapvault import Vault
from ._chapters import chapters
from ._user import User
from ._telekit_dsl.telekit_dsl import TelekitDSL
from ._logger import enable_file_logging
from . import senders
from . import types
from . import styles
from . import parameters

Styles = styles.Styles

from ._version import __version__
    
__all__ = [
    "parameters",
    "senders", 
    "types",
    "styles",

    "Styles", 

    "enable_file_logging",
    "User", 
    "TelekitDSL",
    "Vault", 
    "chapters",

    "example",

    "Server", 
    "Chain", 
    "Handler", 

    "CallbackQueryHandler", 
]