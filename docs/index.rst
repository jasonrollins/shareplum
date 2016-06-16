==============================
SharePlum: Python + SharePoint
==============================

SharePlum is an easier way to work with SharePoint services.  It handles all of the messy parts of dealing with SharePoint and allows you to write clean and Pythonic code.

Example::
    
    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    cred = HttpNtlmAuth('Username', 'Password')
    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)

    list_data = site.GetListItems()

.. toctree::
    :maxdepth: 2

    install
    tutorial
    queries
    objects
    changelog
