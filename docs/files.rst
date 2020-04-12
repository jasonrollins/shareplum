==========
Files
==========

SharePlum can work with files and folders in SharePoint version 2013 and higher using the REST API.  To access this API you need to specify your SharePoint version when creating your Site instance: :: 

    site = Site('https://abc.sharepoint.com/sites/MySharePointSite/', version=Version.v2016, authcookie=authcookie)

Folders
=====

When you create an instance of a folder, you specifiy the folder location.  This folder will be created if it does not exist. ::

    folder = site.Folder('Shared Documents/This Folder')

Files
=====

You can upload a file to the folder with upload_file() ::

    folder.upload_file('Hello', 'new.txt')

or for a binary file ::

    with open(fileName, mode='rb') as file:
	    fileContent = file.read()
    folder.upload_file(fileContent, "filename.bin")

Download a file ::

    folder.download_file('source.txt', 'destination.txt')
    
Read a text file ::

    folder.read_txt_file('new.txt')

Check out a file ::

    folder.check_out('new.txt')

Check in a file ::

    folder.check_in('new.txt', "My check-in comment")

Delete a file ::

    folder.delete_file('new.txt')
