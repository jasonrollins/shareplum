from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
from .test_settings import TEST_SETTINGS
import unittest
import os

# Edit test_server.json file to setup SharePoint Test Server
# Use OS Enviroment Variable TEST_PASSWORD for SharePoint password
# export TEST_PASSWORD=********

class FolderTestCase(unittest.TestCase):

    def setUp(self):
        if TEST_SETTINGS["version"] in ["2014", "2016", "2019", "365"]:
            version=Version.v2016
        else:
            version=Version.v2007

        authcookie = Office365(TEST_SETTINGS["server_url"], username=TEST_SETTINGS["username"], password=os.environ.get('TEST_PASSWORD')).GetCookies()
        self.site = Site(TEST_SETTINGS["site_url"], version=version, authcookie=authcookie)

    def tearDown(self):
        self.site._session.close()

    def test_folder(self):
        print("Testing Folder")
        self.folder = self.site.Folder(TEST_SETTINGS["test_folder"])
        self.folder.upload_file("Hello", "new.txt")
        self.assertEqual(self.folder.get_file("new.txt"), b"Hello")
        self.folder.delete_file("new.txt")