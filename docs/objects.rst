===================
Classes and Methods
===================

Site
====
The main object of the SharePlum library is Site.

.. py:class:: Site(url [, auth=None, verify_ssl=True, ssl_version='TLSv1'])

    Main Site object used to interact with your SharePoint site.

Methods
-------

.. py:function:: AddList(listName, description, templateID)

    Adds a list to your site with the provided name, description, and template.

    Valid Templates include:

    * Announcements
    * Contacts
    * Custom List in Datasheet View
    * DataSources
    * Discussion Board
    * Document Library
    * Events
    * Form Library
    * Issues
    * Links
    * Picture Library
    * Survey
    * Tasks

.. py:function:: DeleteList(listName)

    Delete a list on your site with the provided List Name.

.. py:function:: GetListCollection()

    Returns information about the lists for the Site.

.. py:function:: GetUsers([rowlimit=0])

    Returns information on the userbase of the current Site.

.. py:function:: List(listName)

    Returns a List object for the list with 'listName' on the current Site.

List
====

The List object contains methods for interacting with SharePoint Lists.  Created with Site.List().

Methods
-------

.. py:function:: GetListItems([viewname=None, fields=None, query=None, rowlimit=0])

    * viewname - A valid View Name for the current List.
    * fields - Instead of a View we can pass the individual columns we want.
    * query - A filter we can apply.
    * rowlimit - Limit the number of rows returned

.. py:function:: GetList()

    This is already run when the List object is initialized.  You can access the returned data under self.schema

.. py:function:: GetView(viewname)

    Information about the provided View Name for the current list.

.. py:function:: GetViewCollection()

    This is already run when the List object is initialized.  You can access the returned data under self.views

.. py:function:: UpdateList()

    Does nothing.  TODO.

.. py:function:: UpdateListItems(data, kind)

    Add or edit data on the current List.

    * data - Python Dictionary eg.::

        data = {'Movie': 'Elf', 'Length': '1h 37min'}

    * kind - 'New', 'Update', or 'Delete'

    When using kind='Delete' the data parameter becomes a list of IDs. eg.::
        
        data = ['46, '201', '403', '456']

.. py:function:: GetAttachmentCollection(_id)

    Get a list of attachements for the row with the provided ID.

soap
====

Helper class to build our SOAP requests. You shouldn't have to use this directly.
