from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
import unittest
import json
import os

# Edit test_server.json file to setup SharePoint Test Server
# Use OS Enviroment Variable TEST_PASSWORD for SharePoint password
# export TEST_PASSWORD=********

class ListTestCase(unittest.TestCase):

    def setUp(self):
        with open("test_server.json") as f:
            self.server = json.load(f)

        if self.server["version"] in ["2014", "2016", "2019", "365"]:
            version=Version.v2016
        else:
            version=Version.v2007

        authcookie = Office365(self.server["server_url"], username=self.server["username"], password=os.environ.get('TEST_PASSWORD')).GetCookies()
        self.site = Site(self.server["site_url"], version=version, authcookie=authcookie)
        self.test_list = self.server["test_list"]

    def tearDown(self):
        self.site._session.close()

    def test_create_list(self):
        print("Create List")
        self.site.AddList(self.test_list, description='Great List!', template_id='Custom List')
        self.assertTrue(self.test_list in [i['Title'] for i in self.site.get_list_collection()])

    def test_get_list_fields(self):
        print("Get Fields")
        self.list = self.site.List(self.server["test_list"])
        self.assertIsNotNone(self.list.fields)

    def test_update_list(self):
        print("Update List")
        self.list = self.site.List(self.server["test_list"])
        my_data = data=[{'Title': 'First Row!'},
                        {'Title': 'Another One!'}]
        self.list.UpdateListItems(data=my_data, kind='New')
        self.assertEqual(len(self.list.get_list_items(row_limit=2)), 2)

    def test_users(self):
        print("Test Users")
        self.list = self.site.List(self.server["test_list"])
        self.assertIsNotNone(self.list.users)
        self.site.delete_list(self.server["test_list"])