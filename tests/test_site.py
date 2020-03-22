from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
import unittest
import json
import os

# Edit test_server.json file to setup SharePoint Test Server
# Use OS Enviroment Variable TEST_PASSWORD for SharePoint password
# export TEST_PASSWORD=********

class SiteTestCase(unittest.TestCase):

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

    def test_site_roleassignments(self):
        print("Role Assignments")
        self.assertIsNotNone(self.site.roleassignments)

    def test_site_lists(self):
        print("Site.Lists")
        self.assertIsNotNone(self.site.lists)

    def test_site_users(self):
        print("Site.Users")
        self.assertIsNotNone(self.site.users)
