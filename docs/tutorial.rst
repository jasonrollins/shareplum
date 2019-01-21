========
Tutorial
========

On Premise Authentication
==========================
Getting started is easy.  Just create some credentials you will use to connect to SharePoint with HttpNtlmAuth and pass the url and credentials to the Site object. ::

    from shareplum import Site
    from requests_ntlm import HttpNtlmAuth

    cred = HttpNtlmAuth('Username', 'Password')
    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)

Office 365 Authentication
==========================
For Office 365 Sharepoint is just as easy. The Office365 class grabs a login token from Microsoft's login servers then It logins the Sharepoint site and uses the cookie for Authentication. Make sure to put just the root url for the site in Office365 and add Https:// at start. ::

    from shareplum import Site
    from shareplum import Office365

    authcookie = Office365('https://abc.sharepoint.com', username='username@abc.com', password='password').GetCookies()
    site = Site('https://abc.sharepoint.com/sites/MySharePointSite/', authcookie=authcookie)


Add A List
==========

You can easily create a new list for your site. ::

    site.AddList('My New List', description='Great List!', templateID='Custom List')

Upload Data
===========

Upload content to your list with the UpdateListItems method. ::

    new_list = site.List('My New List')
    my_data = data=[{'Title': 'First Row!'},
                    {'Title': 'Another One!'}]
    new_list.UpdateListItems(data=my_data, kind='New')

Download Data
=============

Retrieve the data from a SharePoint list using GetListItems. ::

    sp_data = new_list.GetListItems()

Retrieve the data from your list by specifiying a SharePoint View, ::

    sp_data = new_list.GetListItems('All Items')

or specifying the fields you want. ::

    sp_data = new_list.GetListItems(fields=['ID', 'Title'])


SharePlum will automatically convert the name of the column that is displayed when you view your list in a web browser to the internal SharePoint name so you don't have to worry about how SharePoint stores the data.

Update List Data
================

You can update data in a SharePoint List easily as well.  You just need the ID number of the row you are updating. ::

    update_data = [{'ID': '1', 'Title': 'My Changed Title'},
                   {'ID': '2', 'Title': 'Another Change'}]
    new_list.UpdateListItems(data=update_data, kind='Update')


Download Files From Document Library
====================================

You can download files from Share Point document libraries with Shareplum.

To download all files in a folder use the code below. Best if you save to an empty local directory. Documents expects the SharePoint folder name or relative url of the Folder. ::

    site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)
    docObj = site.Documents("Folder Name")
    docObj.GetAllFilesInFolder("C:\Local\save\Folder")

If you want to download all the sub folders and files in the sub folders while keeping the folder structure as it is in the root Share Point Document folder
set the include_sub_folders=True like below. ::

    docObj = site.Documents("Folder Name", include_sub_folders=True)


Can also get just one sub folder by the code below. ::

        docObj = site.Documents("Folder Name/Sub Folder Name")

You can get a list of all the sub folders by the code below. This will return a Dictionary of Folder names and the relative url of the folder.
The "folderUrl" returned can be used in all functions that expect a Share Point folder name. ::

        DictOfFolderNames = docObj.GetSubFolders()

If you only want to get a list of what files are in a folder you can use the below code. ::

        site = Site('https://mysharepoint.server.com/sites/MySite', auth=cred)

        # Returns the file names of the folder initialized
        fileNames = docObj.GetDocumentFolderFileNames()

        # if you want to use a different Folder than the one you initialized but is in the same site can use below code
        fileNamesOfDifferentFolder = docObj.GetDocumentFolderFileNames("Folder Name")

You can download specified files if you would like using code below. ::

        docObj.GetFileByRelativeUrl("/FolderName/FileNameToSave.txt", "FileNameToSave.txt", "C:\Local\save\Folder")

Can also use previous functions with GetFileByRelativeUrl function if you would like to see what files you are download and add your own logic to it if you wish. ::

        fileNames = docObj.GetDocumentFolderFileNames("Folder Name")
        for file in fileNames:
            docObj.GetFileByRelativeUrl(file["url"], file["fileName"], "C:\Local\save\Folder")


