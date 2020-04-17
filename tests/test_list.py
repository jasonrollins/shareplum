from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
from .test_settings import TEST_SETTINGS
import unittest
import os

# Edit test_server.json file to setup SharePoint Test Server
# Use OS Enviroment Variable TEST_PASSWORD for SharePoint password
# export TEST_PASSWORD=********

class ListTestCase(unittest.TestCase):

    def setUp(self):
        if TEST_SETTINGS["version"] in ["2014", "2016", "2019", "365"]:
            version=Version.v2016
        else:
            version=Version.v2007

        authcookie = Office365(TEST_SETTINGS["server_url"], username=TEST_SETTINGS["username"], password=os.environ.get('TEST_PASSWORD')).GetCookies()
        self.site = Site(TEST_SETTINGS["site_url"], version=version, authcookie=authcookie)
        self.test_list = TEST_SETTINGS["test_list"]

    def tearDown(self):
        self.site._session.close()

    def test_a_create_list(self):
        print("Create List")
        self.site.AddList(self.test_list, description='Great List!', template_id='Custom List')
        self.assertTrue(self.test_list in [i['Title'] for i in self.site.get_list_collection()])

    def test_b_get_list_fields(self):
        print("Get Fields")
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        self.assertIsNotNone(self.list.fields)

    def test_c_update_list(self):
        print("Update List")
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        my_data = data=[{'Title': 'First Row!'},
                        {'Title': 'Another One!'},
                        {'Title': 'Thrid Row'}]
        self.list.UpdateListItems(data=my_data, kind='New')
        self.assertEqual(len(self.list.get_list_items(row_limit=5)), 3)

    def test_d_delete_row(self):
        print("Delete Row")
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        my_data = data=[1]
        self.list.UpdateListItems(data=my_data, kind='Delete')
        self.assertEqual(len(self.list.get_list_items(row_limit=2)), 2)

    def test_e_get_view(self):
        print("Get View")
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        self.assertEqual(len(self.list.GetListItems("All Items")), 2)

    def test_f_query_list(self):
        print('Test Query')
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        query = {'Where': [('Eq', 'Title', 'Another One!')]}
        items = self.list.GetListItems(fields=['Title'], query=query)
        self.assertEqual(len(items), 1)

    def test_g_users(self):
        print("Test Users")
        self.list = self.site.List(TEST_SETTINGS["test_list"])
        self.assertIsNotNone(self.list.users)
        self.site.delete_list(TEST_SETTINGS["test_list"])