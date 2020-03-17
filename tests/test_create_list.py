from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
import unittest
import json
import os

# Edit test_server.json file to setup SharePoint Test Server
# Use OS Enviroment Variable TEST_PASSWORD for SharePoint password
# export TEST_PASSWORD=********

class MyTestCase(unittest.TestCase):

    def setUp(self):
        with open("test_server.json") as f:
            self.server = json.load(f)

        if self.server["version"] in ["2014", "2016", "2019", "365"]:
            version=Version.v2016
        else:
            version=Version.v2007

        authcookie = Office365(self.server["server_url"], username=self.server["username"], password=os.environ.get('TEST_PASSWORD')).GetCookies()
        self.site = Site(self.server["site_url"], version=version, authcookie=authcookie)

    def tearDown(self):
        self.site._session.close()

    def test_site_roleassignments(self):
        self.assertIsNotNone(self.site.roleassignments)

    def test_site_lists(self):
        self.assertIsNotNone(self.site.lists)

    def test_site_users(self):
        self.assertIsNotNone(self.site.users)

    def test_get_list_items(self):
        self.list = self.site.List(self.server["test_list"])
        self.assertEqual(len(self.list.get_list_items(row_limit=2)), 2)

    def test_get_list_fields(self):
        self.list = self.site.List(self.server["test_list"])
        self.assertIsNotNone(self.list.fields)

    def test_users(self):
        self.list = self.site.List(self.server["test_list"])
        self.assertIsNotNone(self.list.users)

    def test_folder(self):
        self.folder = self.site.Folder(self.server["test_folder"])
        self.folder.upload_file("Hello", "new.txt")
        self.assertEqual(self.folder.get_file("new.txt"), "Hello")
        self.folder.delete_file("new.txt")
