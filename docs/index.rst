==============================
SharePlum: Python + SharePoint
==============================

SharePlum is an easier way to work with SharePoint services.  It handles all of the messy parts of dealing with SharePoint and allows you to write clean and Pythonic code.

::
    
    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    cred = HttpNtlmAuth('Username', 'Password')
    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)

    list_data = site.GetListItems()


You can easily create a new list.

::

    site.AddList('My New List', description='Great List!', templateID='Custom List')

And upload content to it.

::

    new_list = site.List('My New List')
    my_data = data=[{'Title': 'First Row!'},
                    {'Title': 'Another One!'}
    new_list.UpdateListItems(data=my_data, kind='New')

Then download the data by specifiying a SharePoint View,

::

    sp_data = new_list.GetListItems('All Items')

or specifying the fields you want.

::

    sp_data = new_list.GetListItems(fields=['ID', 'Title'])


SharePlum will automatically convert the name of the column that is displayed to the internal SharePoint name so you don't have to worry about how SharePoint stores the data.

You can update data in a SharePoint List easily as well.  You just need the ID number of the row you are updating.

::

    update_data = [{'ID': '1', 'Title': 'My Changed Title'},
                   {'ID': '2', 'Title': 'Another Change'}]
    new_list.UpdateListItems(data=update_data, kind='Update')

