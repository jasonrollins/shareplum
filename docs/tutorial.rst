Tutorial
========

Getting started is easy.  Just create some credentials you will use to connect to the SharePoint with HttpNtlmAuth and pass the url and credentials to the Site object.

::
    
    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    cred = HttpNtlmAuth('Username', 'Password')
    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)


Add A List
^^^^^^^^^^

You can easily create a new list for your site.

::

    site.AddList('My New List', description='Great List!', templateID='Custom List')

Upload Data
^^^^^^^^^^^

Upload content to your list with the UpdateListItems method.

::

    new_list = site.List('My New List')
    my_data = data=[{'Title': 'First Row!'},
                    {'Title': 'Another One!'}
    new_list.UpdateListItems(data=my_data, kind='New')

Download Data
^^^^^^^^^^^^^

Download the data from your list with GetListItems by specifiying a SharePoint View,

::

    sp_data = new_list.GetListItems('All Items')

or specifying the fields you want.

::

    sp_data = new_list.GetListItems(fields=['ID', 'Title'])


SharePlum will automatically convert the name of the column that is displayed when you view your list in a web browser to the internal SharePoint name so you don't have to worry about how SharePoint stores the data.

Update List Data
^^^^^^^^^^^^^^^^

You can update data in a SharePoint List easily as well.  You just need the ID number of the row you are updating.

::

    update_data = [{'ID': '1', 'Title': 'My Changed Title'},
                   {'ID': '2', 'Title': 'Another Change'}]
    new_list.UpdateListItems(data=update_data, kind='Update')


