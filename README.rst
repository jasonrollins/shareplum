==========
SharePlum
==========

shareplum allows a more pythonic approach to reading
from and wrting to SharePoint site contents.

Usage:
::

    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    auth = HttpNtlmAuth('DIR\\username', 'password')
    site = Site('https://abc.com/sites/MySharePointSite/', auth=auth)
    sp_list = site.List('list name')
    data = sp_list.GetListItems('All Items', rowlimit=200)
