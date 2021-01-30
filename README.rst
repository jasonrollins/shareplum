PROJECT STATUS
===================

I have not had access to a SharePoint server for a while now and I do not feel that I can support this library in any reasonable fashion.  I will still accept pull requests and respond to issues as much as I can, but please be aware that I am no longer capapable of testing most of these changes.

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

Authenticate to Office365 Sharepoint
------------------------------------

::

    from shareplum import Site
    from shareplum import Office365

    authcookie = Office365('https://abc.sharepoint.com', username='username@abc.com', password='password').GetCookies()
    site = Site('https://abc.sharepoint.com/sites/MySharePointSite/', authcookie=authcookie)
    sp_list = site.List('list name')
    data = sp_list.GetListItems('All Items', rowlimit=200)


Access REST API
------------------------------------

::

    from shareplum import Site
    from shareplum import Office365
    from shareplum.site import Version

    authcookie = Office365('https://abc.sharepoint.com', username='username@abc.com', password='password').GetCookies()
    site = Site('https://abc.sharepoint.com/sites/MySharePointSite/', version=Version.v2016, authcookie=authcookie)
    folder = site.Folder('Shared Documents/This Folder')
    folder.upload_file('Hello', 'new.txt')
    folder.get_file('new.txt')
    folder.check_out('new.txt')
    folder.check_in('new.txt', "My check-in comment")
    folder.delete_file('new.txt')


Features
--------

- Reading and writing data to SharePoint lists using Python Dictionaries.
- Automatic conversion between SharePoint internal names and displayed names.
- Using Queries to filter data when retrieving List Items.
- Automatic conversion of data types.
- Supports Users datatype.
- Supports Office365 Sharepoint sites.
- Supports Folder and File operations with the REST API. (Requires SharePoint 2013 or newer)

Documentation
-------------

`Read the Docs <http://shareplum.readthedocs.org/en/latest/>`_

Contribute
----------

- `Issue Tracker <http://github.com/jasonrollins/shareplum/issues>`_
- `Source Code <http://github.com/jasonrollins/shareplum>`_

Unit Tests
^^^^^^^^^^

This package uses python unittest.
To run the unit tests, first copy tests/test_settings.py as tests/local_test_seetings.py and edit the contents to point at your sharepoint.
Second export your sharepoint password as an environment variable 'TEST_PASSWORD'
Then from the root folder run:

::

    python -m unittest disover  # all tests
    python -m unittest tests.test_site  # all site tests

License
-------

This project is licensed under the MIT license.
