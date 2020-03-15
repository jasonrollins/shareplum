# SharePlum
# This library simplfies the code necessary
# to automate interactions with a SharePoint
# server using python
from .office365 import Office365  # noqa: F401
from .site import Site  # noqa: F401
from .version import __version__  # noqa: F401

__all__ = ["site", "office365"]

__title__ = "SharePlum SharePoint Library"
__author__ = "Jason Rollins"
