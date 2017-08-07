==============================
SharePlum: Python + SharePoint
==============================

SharePlum is an easier way to work with SharePoint services.  It handles all of the messy parts of dealing with SharePoint and allows you to write clean and Pythonic code.

Example::
    
    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    cred = HttpNtlmAuth('Username', 'Password')
    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)
    sp_list = site.List('list name')

    list_data = sp_list.GetListItems()

.. toctree::
    :maxdepth: 2

    install
    tutorial
    queries
    advanced
    objects
    changelog
