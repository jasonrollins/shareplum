from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests
from requests.packages.urllib3.util.retry import Retry
from requests_toolbelt import SSLAdapter
from lxml import etree
# import defusedxml.ElementTree as etree

from .errors import ShareplumRequestError
from .request_helper import get, post
from .list import _List2007, _List365
from .folder import _Folder
from .soap import Soap
from .version import __version__

from enum import Enum


# SharePoint Versions
class Version(Enum):
    v2007 = 1
    v2010 = 2
    v2013 = 3
    v2016 = 4
    v2019 = 5
    v365 = 6


class _Site2007:

    def __init__(self,
                 site_url,  # type: str
                 auth=None,  # type: Optional[Any]
                 authcookie=None,  # type: Optional[requests.cookies.RequestsCookieJar]
                 verify_ssl=True,  # type: bool
                 ssl_version=None,  # type: Optional[float]
                 huge_tree=False,  # type: bool
                 timeout=None,  # type: Optional[int]
                 retry=None):
        self.site_url = site_url
        self._verify_ssl = verify_ssl

        if retry is None:
            retry = Retry(total=5,
                        read=5,
                        connect=5,
                        backoff_factor=0.3,
                        status_forcelist=[500, 502, 503, 504])

        http_adaptor = requests.adapters.HTTPAdapter(max_retries=retry)
        https_adaptor = http_adaptor

        self._session = requests.Session()
        if ssl_version is not None:
            https_adaptor = SSLAdapter(ssl_version, max_retries=retry)

        self._session.mount("https://", https_adaptor)
        self._session.mount("http://", http_adaptor)

        self._session.headers.update({"user-agent": "shareplum/%s" % __version__})

        if authcookie is not None:
            self._session.cookies = authcookie
        else:
            self._session.auth = auth

        self.huge_tree = huge_tree

        self.timeout = timeout

        self.last_request = None  # type: Optional[str]

        self._services_url = {
            "Alerts": "/_vti_bin/Alerts.asmx",
            "Authentication": "/_vti_bin/Authentication.asmx",
            "Copy": "/_vti_bin/Copy.asmx",
            "Dws": "/_vti_bin/Dws.asmx",
            "Forms": "/_vti_bin/Forms.asmx",
            "Imaging": "/_vti_bin/Imaging.asmx",
            "DspSts": "/_vti_bin/DspSts.asmx",
            "Lists": "/_vti_bin/lists.asmx",
            "Meetings": "/_vti_bin/Meetings.asmx",
            "People": "/_vti_bin/People.asmx",
            "Permissions": "/_vti_bin/Permissions.asmx",
            "SiteData": "/_vti_bin/SiteData.asmx",
            "Sites": "/_vti_bin/Sites.asmx",
            "Search": "/_vti_bin/Search.asmx",
            "UserGroup": "/_vti_bin/usergroup.asmx",
            "Versions": "/_vti_bin/Versions.asmx",
            "Views": "/_vti_bin/Views.asmx",
            "WebPartPages": "/_vti_bin/WebPartPages.asmx",
            "Webs": "/_vti_bin/Webs.asmx",
        }  # type: Dict[str, str]

        self.site_info = self.get_site()
        self.users = self.get_users()
        self.version = "2007"  # For Debugging

    def _url(self, service):
        # type: (str) -> str
        """Full SharePoint Service URL"""
        return "".join([self.site_url, self._services_url[service]])

    def _headers(self, soap_action):
        # type: (str) -> Dict[str, str]
        headers = {
            "Content-Type": "text/xml; charset=UTF-8",
            "SOAPAction": "http://schemas.microsoft.com/sharepoint/soap/" + soap_action,
        }
        return headers

    # This is part of List but seems awkward under the List Method
    def add_list(self, list_name, description, template_id):
        # type: (str, str, str) -> Any
        """Create a new List
           Provide: List Name, List Description, and List Template
           Templates Include:
               Announcements
               Contacts
               Custom List
               Custom List in Datasheet View
               DataSources
               Discussion Board
               Document Library
               Events
               Form Library
               Issues
               Links
               Picture Library
               Survey
               Tasks
        """
        template_ids = {
            "Announcements": "104",
            "Contacts": "105",
            "Custom List": "100",
            "Custom List in Datasheet View": "120",
            "DataSources": "110",
            "Discussion Board": "108",
            "Document Library": "101",
            "Events": "106",
            "Form Library": "115",
            "Issues": "1100",
            "Links": "103",
            "Picture Library": "109",
            "Survey": "102",
            "Tasks": "107",
        }

        # Let's automatically convert the different
        # ways we can select the template_id
        if type(template_id) == int:
            template_id = str(template_id)
        elif type(template_id) == str:
            if template_id.isdigit():
                pass
            else:
                template_id = template_ids[template_id]

        # Build Request
        soap_request = Soap("AddList")
        soap_request.add_parameter("listName", list_name)
        soap_request.add_parameter("description", description)
        soap_request.add_parameter("templateID", template_id)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("AddList"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        return response.text

    def delete_list(self, list_name):
        # type: (str) -> Optional[str]
        """Delete a List with given name"""

        # Build Request
        soap_request = Soap("DeleteList")
        soap_request.add_parameter("listName", list_name)
        self.last_request = str(soap_request)

        # Send Request
        post(self._session,
             url=self._url("Lists"),
             headers=self._headers("DeleteList"),
             data=str(soap_request).encode("utf-8"),
             verify=self._verify_ssl,
             timeout=self.timeout)

    def get_form_collection(self, list_name):

        # Build Request
        soap_request = Soap("GetFormCollection")
        soap_request.add_parameter("listName", list_name)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Forms"),
                        headers=self._headers("GetFormCollection"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        items = envelope[0][0][0][0]
        data = []
        for _item in items:
            data.append({k: v for (k, v) in _item.items()})

        return data

    def get_site(self):

        # Build Request
        soap_request = Soap("GetSite")
        soap_request.add_parameter("SiteUrl", self.site_url)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Sites"),
                        headers=self._headers("GetSite"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        data = envelope[0][0][0]

        # TODO: Not sure what to do with this, so just return the text
        return data.text

    def get_list_templates(self):

        # Build Request
        soap_request = Soap("GetListTemplates")
        soap_request.add_parameter("GetListTemplates")
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Webs"),
                        headers=self._headers("GetListTemplates"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        lists = envelope[0][0][0][0]
        data = []
        for _list in lists:
            data.append({k: v for (k, v) in _list.items()})

        return data

    def get_site_templates(self, lcid="1033"):

        # Build Request
        soap_request = Soap("GetSiteTemplates")
        soap_request.add_parameter("LCID", lcid)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Sites"),
                        headers=self._headers("GetSiteTemplates"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        return response
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        lists = envelope[0][0][1]
        data = []
        for _list in lists:
            data.append({k: v for (k, v) in _list.items()})

        return data

    def get_list_collection(self):
        # type: () -> Optional[List[Dict[str, str]]]
        """Returns List information for current Site"""
        # Build Request
        soap_request = Soap("GetListCollection")
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("SiteData"),
                        headers=self._headers("GetListCollection"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        # TODO: Verify if this works on Sharepoint lists with validation
        lists = envelope[0][0][1]
        data = []
        for _list in lists:
            _list_data = {}
            for item in _list:
                key = item.tag.replace("{http://schemas.microsoft.com/sharepoint/soap/}", "")
                value = item.text
                _list_data[key] = value
            data.append(_list_data)

        return data

    def get_users(self, rowlimit=0):
        # type: (int) -> Optional[Dict[str, Dict[str, str]]]
        """Get Items from current list
           rowlimit defaulted to 0 (no limit)
        """

        # Build Request
        soap_request = Soap("GetListItems")
        soap_request.add_parameter("listName", "UserInfo")

        # Set Row Limit
        soap_request.add_parameter("rowLimit", str(rowlimit))
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(self._url("Lists"),
                                      headers=self._headers("GetListItems"),
                                      data=str(soap_request).encode("utf-8"),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout,
                                      )
        if response.status_code == 404 and requests.post(self._url("Lists")).status_code == 200:
            raise ShareplumRequestError("get_users received a 404 for the SOAP request "
                                        "even though the URL {} is accessible; this error code in this context means "
                                        "the authorization is bad.".format(self._url("Lists")))
        response.raise_for_status()

        # Parse Response
        try:
            envelope = etree.fromstring(response.text.encode("utf-8"),
                                        parser=etree.XMLParser(huge_tree=self.huge_tree,
                                        recover=True))
        except Exception as e:
            raise requests.ConnectionError("GetUsers GetListItems response failed to parse correctly: " + str(e))
        # TODO: Verify if this works on Sharepoint lists with validation
        listitems = envelope[0][0][0][0][0]
        data = []
        for row in listitems:
            # Strip the 'ows_' from the beginning with key[4:]
            data.append({key[4:]: value for (key, value) in row.items() if key[4:]})

        return {
            "py": {i["ImnName"]: i["ID"] + ";#" + i["ImnName"] for i in data},
            "sp": {i["ID"] + ";#" + i["ImnName"]: i["ImnName"] for i in data},
        }

    # SharePoint Method Objects
    # Not the best name as it could clash with the built-in list()
    def list(self, list_name, exclude_hidden_fields=False):
        # type: (str, bool) -> _List2007
        """Sharepoint Lists Web Service
           Microsoft Developer Network:
           The Lists Web service provides methods for working
           with SharePoint lists, content types, list items, and files.
        """

        return _List2007(
            self._session,
            list_name,
            self._url,
            self._verify_ssl,
            self.users,
            self.huge_tree,
            self.timeout,
            exclude_hidden_fields=exclude_hidden_fields,
            site_url=self.site_url,
        )

    # Legacy API
    List = list
    GetUsers = get_users
    GetListCollection = get_list_collection
    DeleteList = delete_list
    AddList = add_list


class _Site365(_Site2007):
    def __init__(self,
                 site_url,  # type: str
                 auth=None,  # type: Optional[Any]
                 authcookie=None,  # type: Optional[requests.cookies.RequestsCookieJar]
                 verify_ssl=True,  # type: bool
                 ssl_version=None,  # type: Optional[float]
                 huge_tree=False,  # type: bool
                 timeout=None):  # type: Optional[int]
        super().__init__(site_url, auth, authcookie, verify_ssl, ssl_version, huge_tree, timeout)

        self._session.headers.update({'Accept': 'application/json',
                                      'Content-Type': 'application/json;odata=nometadata'})
        self.version = "v365"

    @property
    def info(self):
        response = get(self._session, self.site_url + "/_api/site")
        return response.json()

    def Folder(self, folder_name):
        """Sharepoint Folder Web Service
        """
        return _Folder(self._session, folder_name, self.site_url, timeout=self.timeout)

    def _get_form_digest_value(self):
        response = post(self._session, self.site_url + "/_api/contextinfo")
        return response.json()['FormDigestValue']

    @property
    def contextinfo(self):
        response = post(self._session, self.site_url + "/_api/contextinfo")
        return response.json()

    @property
    def contenttypes(self):
        response = get(self._session, self.site_url + "/_api/web/contenttypes")
        return response.json()['value']

    @property
    def eventreceivers(self):
        response = get(self._session, self.site_url + "/_api/web/eventreceivers")
        return response.json()['value']

    @property
    def features(self):
        response = get(self._session, self.site_url + "/_api/web/features")
        return response.json()['value']

    @property
    def fields(self):
        response = get(self._session, self.site_url + "/_api/web/fields")
        return response.json()['value']

    @property
    def lists(self):
        return self.GetListCollection()

    # This is a duplicate, but in REST
    # def GetListCollection(self):
    #     response = get(self._session, self.site_url + "/_api/web/lists")
    #     data = json.loads(response.text)
    #     return data['value']

    @property
    def siteusers(self):
        return self.GetUsers()

    def GetUsers(self, row_limit=None):
        response = get(self._session, self.site_url + "/_api/web/siteusers")
        return response.json()['value']

    @property
    def groups(self):
        response = get(self._session, self.site_url + "/_api/web/sitegroups")
        return response.json()['value']

    @property
    def roleassignments(self):
        response = get(self._session, self.site_url + "/_api/web/roleassignments")
        return response.json()['value']

    @property
    def web(self):
        response = get(self._session, self.site_url + "/_api/web")
        return response.json()['value']

    # SharePoint Method Objects
    # Not the best name as it could clash with the built-in list()
    def list(self, list_name, exclude_hidden_fields=False):
        # type: (str, bool) -> _List365
        """Sharepoint Lists Web Service
           Microsoft Developer Network:
           The Lists Web service provides methods for working
           with SharePoint lists, content types, list items, and files.
        """

        return _List365(
            self._session,
            list_name,
            self._url,
            self._verify_ssl,
            self.users,
            self.huge_tree,
            self.timeout,
            exclude_hidden_fields=exclude_hidden_fields,
            site_url=self.site_url,
        )

    # Legacy API
    List = list


def Site(site_url,  # type: str
         version=Version.v2007,
         auth=None,  # type: Optional[Any]
         authcookie=None,  # type: Optional[requests.cookies.RequestsCookieJar]
         verify_ssl=True,  # type: bool
         ssl_version=None,  # type: Optional[float]
         huge_tree=False,  # type: bool
         timeout=None):  # type: Optional[int]

    # We ask for the various versions of SharePoint with 2010 as default
    # Multiple Version are allowed, but only 2010, 2013, and 365 are implemented
    if version == Version.v2007:
        return _Site2007(site_url,
                         auth,
                         authcookie,
                         verify_ssl,
                         ssl_version,
                         huge_tree,
                         timeout)

    elif version == Version.v2010:
        return _Site2007(site_url,
                         auth,
                         authcookie,
                         verify_ssl,
                         ssl_version,
                         huge_tree,
                         timeout)

    elif version == Version.v2013:
        return _Site365(site_url,
                        auth,
                        authcookie,
                        verify_ssl,
                        ssl_version,
                        huge_tree,
                        timeout)

    elif version == Version.v2016:
        return _Site365(site_url,
                        auth,
                        authcookie,
                        verify_ssl,
                        ssl_version,
                        huge_tree,
                        timeout)

    elif version == Version.v2019:
        return _Site365(site_url,
                        auth,
                        authcookie,
                        verify_ssl,
                        ssl_version,
                        huge_tree,
                        timeout)

    elif version == Version.v365:
        return _Site365(site_url,
                        auth,
                        authcookie,
                        verify_ssl,
                        ssl_version,
                        huge_tree,
                        timeout)
