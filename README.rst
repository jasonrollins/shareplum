SharePlum
==========

SharePlum is an easier way to work with SharePoint services. It handles all of the messy parts of dealing with SharePoint and allows you to write clean and Pythonic code.

Usage
-----

::

    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    auth = HttpNtlmAuth('DIR\\username', 'password')
    site = Site('https://abc.com/sites/MySharePointSite/', auth=auth)
    sp_list = site.List('list name')
    data = sp_list.GetListItems('All Items', rowlimit=200)

Features
--------

- Reading and writing data to SharePoint lists using Python Dictionaries.
- Automatic conversion between SharePoint internal names and displayed names.
- Automatic conversion of data types.

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
