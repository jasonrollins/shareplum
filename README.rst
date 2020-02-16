SharePlum
==========

If you are using SharePoint 2016 or greater use `SharePlum2 <https://github.com/jasonrollins/shareplum2>`_ instead.  This library is no longer actively maintined.  Only use this library if you are using SharePoint 2013 or earlier.

SharePlum is an easier way to work with SharePoint services. It handles all of the messy parts of dealing with SharePoint and allows you to write clean and Pythonic code.

Why are there 2 versions?
-------------------------

1. The SOAP API is obsolete.
2. I only have access to SharePoint365 so I can not test any changes to this library.
3. Contributors to this library have submitted PRs that would not work for older versions of SharePoint.
4. Users of the SharePlum library are limited to the features provided by the SOAP api. 

Usage
-----

::

    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    auth = HttpNtlmAuth('DIR\\username', 'password')
    site = Site('https://abc.com/sites/MySharePointSite/', auth=auth)
    sp_list = site.List('list name')
    data = sp_list.GetListItems('All Items', rowlimit=200)

Authenticate to Office365 Sharepoint
------------------------------------

::

    from shareplum import Site
    from shareplum import Office365

    authcookie = Office365('https://abc.sharepoint.com', username='username@abc.com', password='password').GetCookies()
    site = Site('https://abc.sharepoint.com/sites/MySharePointSite/', authcookie=authcookie)
    sp_list = site.List('list name')
    data = sp_list.GetListItems('All Items', rowlimit=200)



Features
--------

- Reading and writing data to SharePoint lists using Python Dictionaries.
- Automatic conversion between SharePoint internal names and displayed names.
- Using Queries to filter data when retrieving List Items.
- Automatic conversion of data types.
- Supports Users datatype.
- Supports Office365 Sharepoint sites.

Documentation
-------------

`Read the Docs <http://shareplum.readthedocs.org/en/latest/>`_

Contribute
----------

- `Issue Tracker <http://github.com/jasonrollins/shareplum/issues>`_
- `Source Code <http://github.com/jasonrollins/shareplum>`_

License
-------

This project is licensed under the MIT license.
