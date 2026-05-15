from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telekit import Handler as _Base
else:
    _Base = object

class Trait(_Base):
    """Base for all traits."""
    pass