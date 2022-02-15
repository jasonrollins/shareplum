import re
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from .request_helper import post
import requests
import json
from lxml import etree

from .soap import Soap

# import defusedxml.ElementTree as etree


class _List2007:
    """Sharepoint Lists Web Service
       Microsoft Developer Network:
       The Lists Web service provides methods for working
       with SharePoint lists, content types, list items, and files.
    """

    def __init__(
        self,
        session,  # type: requests.Session
        list_name,  # type: str
        url,  # type: Callable[[str], str]
        verify_ssl,  # type: bool
        users,  # type: Optional[Dict]
        huge_tree,  # type: bool
        timeout,  # type: Optional[int]
        exclude_hidden_fields=False,  # type: bool
        site_url=None,
    ):
        # type: (...) -> None
        self._session = session
        self.list_name = list_name
        self._url = url
        self._verify_ssl = verify_ssl
        self.users = users
        self.huge_tree = huge_tree
        self.timeout = timeout
        self._exclude_hidden_fields = exclude_hidden_fields
        # List Info
        self.fields = []  # type: List[Dict[str, str]]
        self.regional_settings = {}  # type: Dict[str, str]
        self.server_settings = {}  # type: Dict[str, str]
        self.get_list()
        self.views = self.get_view_collection()
        self.version = "2007"

        # fields sometimes share the same displayname
        # filtering fields to only contain visible fields
        # minimizes the chance of a one field hiding another
        if exclude_hidden_fields:
            self.fields = [field for field in self.fields if field.get("Hidden", "FALSE") == "FALSE"]

        self._sp_cols = {i["Name"]: {"name": i["DisplayName"], "type": i["Type"]} for i in self.fields}
        self._disp_cols = {i["DisplayName"]: {"name": i["Name"], "type": i["Type"]} for i in self.fields}

        title_col = self._sp_cols["Title"]["name"]
        title_type = self._sp_cols["Title"]["type"]
        self._disp_cols[title_col] = {"name": "Title", "type": title_type}
        self.last_request = None  # type: Optional[str]
        self.date_format = re.compile("[0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+:[0-9]+")

    def _headers(self, soapaction):
        # type: (str) -> Dict[str,str]
        headers = {
            "Content-Type": "text/xml; charset=UTF-8",
            "SOAPAction": "http://schemas.microsoft.com/sharepoint/soap/" + soapaction,
        }
        return headers

    def _mutate_to_internal(self, data):
        # type: (List[Dict]) -> None
        """From 'Column Title' to 'Column_x0020_Title'"""
        for _dict in data:
            keys = list(_dict.keys())[:]
            for key in keys:
                if key not in self._disp_cols:
                    raise Exception(key + " not a column in current List.")
                _dict[self._disp_cols[key]["name"]] = self._sp_type(key, _dict.pop(key))

    def _convert_to_internal(self, data):
        # type: (List[Dict]) -> None
        """From 'Column Title' to 'Column_x0020_Title'"""
        new_data = []
        for _dict in data:
            keys = list(_dict.keys())[:]
            new_dict = dict()
            for key in keys:
                if key not in self._disp_cols:
                    raise Exception(key + " not a column in current List.")
                new_dict[self._disp_cols[key]["name"]] = self._sp_type(key, _dict[key])
            new_data.append(new_dict)

        return new_data

    def _convert_to_display(self, data):
        # type: (List[Dict]) -> None
        """From 'Column_x0020_Title' to  'Column Title'"""
        for _dict in data:
            keys = list(_dict.keys())[:]
            for key in keys:
                if key not in self._sp_cols:
                    raise Exception(key + " not a column in current List.")
                _dict[self._sp_cols[key]["name"]] = self._python_type(key, _dict.pop(key))

    def _python_type(self, key, value):
        # type: (str, Any) -> Any
        """Returns proper type from the schema"""
        try:
            field_type = self._sp_cols[key]["type"]
            if field_type in ["Number", "Currency"]:
                return float(value)
            elif field_type == "DateTime":

                # Need to remove the '123;#' from created dates, but we will do it for all dates
                # self.date_format = re.compile('\d+-\d+-\d+ \d+:\d+:\d+')
                match = self.date_format.search(value)
                if match:
                    value = match.group(0)

                # NOTE: I used to round this just date (7/28/2018)
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif field_type == "Boolean":
                if value == "1":
                    return "Yes"
                elif value == "0":
                    return "No"
                else:
                    return ""
            elif field_type in ("User", "UserMulti"):
                # Sometimes the User no longer exists or
                # has a diffrent ID number so we just remove the "123;#"
                # from the beginning of their name
                if self.users and value in self.users["sp"]:
                    return self.users["sp"][value]
                elif "#" in value:
                    users = []
                    for i, value in enumerate(value.split(';#')):
                        if i % 2 == 0:
                            user = '#%s' % value
                        else:
                            user += ';#%s' % value
                            users.append(user)
                    return users
                else:
                    return value
            else:
                return value
        except AttributeError:
            # TODO: log me
            return value

    def _sp_type(self, key, value):
        # type: (str, Any) -> Any
        """Returns proper type from the schema"""
        try:
            field_type = self._disp_cols[key]["type"]
            if field_type in ["Number", "Currency"]:
                return value
            elif field_type == "DateTime":
                return value.strftime("%Y-%m-%d %H:%M:%S")
            elif field_type == "Boolean":
                if value == "Yes":
                    return "1"
                elif value == "No":
                    return "0"
                else:
                    raise Exception("%s not a valid Boolean Value, only 'Yes' or 'No'" % value)
            elif self.users and field_type == "User":
                return self.users["py"][value]
            else:
                return value
        except AttributeError:
            # TODO: Log me
            return value

    def get_list_items(
        self,
        view_name=None,  # type: Optional[str]
        fields=None,  # type: Optional[List[str]]
        query=None,  # type: Optional[Dict]
        row_limit=0,  # type: int
        debug=False,  # type: bool
    ):
        # type: (...) -> Optional[Any]
        """Get Items from current list
           row_limit defaulted to 0 (unlimited)
        """

        # Build Request
        soap_request = Soap("GetListItems")
        soap_request.add_parameter("listName", self.list_name)
        # Convert Displayed View Name to View ID
        if view_name:
            soap_request.add_parameter("viewName", self.views[view_name]["Name"][1:-1])

        # Add viewFields
        if fields:
            # Convert to SharePoint Style Column Names
            for i, val in enumerate(fields):
                fields[i] = self._disp_cols[val]["name"]
            viewfields = fields
            soap_request.add_view_fields(fields)
            # Check for viewname and query
            if [view_name, query] == [None, None]:
                # Add a query if the viewname and query are not provided
                # We sort by 'ID' here Ascending is the default
                soap_request.add_query({"OrderBy": ["ID"]})

        elif view_name:
            viewfields = self.get_view(view_name)["fields"]
        else:
            # No fields or views provided so get everything
            viewfields = [x for x in self._sp_cols]

        # Add query
        if query:
            modified_query = dict()
            where = etree.Element('Where')

            parents = [where]
            if "Where" in query:
                where = etree.Element("Where")

                parents = [where]
                for _i, field in enumerate(query["Where"]):
                    if field == "And":
                        parents.append(etree.SubElement(parents[-1], "And"))
                    elif field == "Or":
                        if parents[-1].tag == "Or":
                            parents.pop()
                        parents.append(etree.SubElement(parents[-1], "Or"))
                    else:
                        _type = etree.SubElement(parents[-1], field[0])
                        field_ref = etree.SubElement(_type, "FieldRef")
                        field_ref.set("Name", self._disp_cols[field[1]]["name"])
                        value = etree.SubElement(_type, "Value")
                        value.set("Type", self._disp_cols[field[1]]["type"])
                        value.text = self._sp_type(field[1], field[2])

                # query["Where"] = where
                modified_query["Where"] = where

            soap_request.add_query(modified_query)

        # Set Row Limit
        soap_request.add_parameter("rowLimit", str(row_limit))
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("GetListItems"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        # Parse Response
        # TODO: Verify if this works with Sharepoint lists with validation
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        listitems = envelope[0][0][0][0][0]
        data = []
        for row in listitems:
            # Strip the 'ows_' from the beginning with key[4:]
            data.append({key[4:]: value for (key, value) in row.items() if key[4:] in viewfields})

        self._convert_to_display(data)

        if debug:
            return response
        else:
            return data

    def get_list(self):  # type: () -> None
        """Get Info on Current List
           This is run in __init__ so you don't
           have to run it again.
           Access from self.schema
        """

        # Build Request
        soap_request = Soap("GetList")
        soap_request.add_parameter("listName", self.list_name)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("GetList"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        # Parse Response
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))  # type: etree.ElementTree
        (fields, regional_settings, server_settings) = self.parse_list_envelope(envelope)
        self.fields += fields
        self.regional_settings.update(regional_settings)
        self.server_settings.update(server_settings)

    @staticmethod
    def parse_list_envelope(envelope):
        # type: (etree.ElementTree) -> Tuple[List[Dict[str, Any]], Dict[str, str], Dict[str, str]]
        _list = envelope[0][0][0][0]
        fields = []
        regional_settings = dict()
        server_settings = dict()

        # info = {key: value for (key, value) in _list.items()}
        for row in _list.xpath(
            "//*[re:test(local-name(), '.*Fields.*')]", namespaces={"re": "http://exslt.org/regular-expressions"}
        )[0].getchildren():
            fields.append({key: value for (key, value) in row.items()})

        for setting in _list.xpath(
            "//*[re:test(local-name(), '.*RegionalSettings.*')]",
            namespaces={"re": "http://exslt.org/regular-expressions"},
        )[0].getchildren():
            regional_settings[setting.tag.strip("{http://schemas.microsoft.com/sharepoint/soap/}")] = setting.text

        for setting in _list.xpath(
            "//*[re:test(local-name(), '.*ServerSettings.*')]",
            namespaces={"re": "http://exslt.org/regular-expressions"},
        )[0].getchildren():
            server_settings[setting.tag.strip("{http://schemas.microsoft.com/sharepoint/soap/}")] = setting.text

        return fields, regional_settings, server_settings

    def get_view(self, view_name):  # type: (str)  -> Optional[Dict]
        """Get Info on View Name
        """

        # Build Request
        soap_request = Soap("GetView")
        soap_request.add_parameter("listName", self.list_name)

        if not view_name:
            views = self.get_view_collection()
            if views:
                for v in views:
                    if "DefaultView" in v:
                        if views[v]["DefaultView"] == "TRUE":
                            view_name = v
                            break

        if self.list_name not in ["UserInfo", "User Information List"] and self.views:
            soap_request.add_parameter("viewName", self.views[view_name]["Name"][1:-1])
        else:
            soap_request.add_parameter("viewName", view_name)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Views"),
                        headers=self._headers("GetView"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        # Parse Response
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))  # type: etree.ElementTree
        # TODO: Fix me? Should this use XPath too?
        view = envelope[0][0][0][0]
        info = {key: value for (key, value) in view.items()}
        fields = [x.items()[0][1] for x in view[1]]
        return {"info": info, "fields": fields}

    def get_view_collection(self):  # type: () -> Optional[Dict[str, Dict[str, str]]]
        """Get Views for Current List
           This is run in __init__ so you don't
           have to run it again.
           Access from self.views
        """

        # Build Request
        soap_request = Soap("GetViewCollection")
        soap_request.add_parameter("listName", self.list_name)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Views"),
                        headers=self._headers("GetViewCollection"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        views = envelope[0][0][0][0]
        data = []
        for row in views.getchildren():
            data.append({key: value for (key, value) in row.items()})
        view = {}
        for row in data:
            view[row["DisplayName"]] = row
        return view

    def get_version_collection(self, list_id, item_id, field_name):  # type: () -> List[Dict[str, str]]

        # Build Request
        soap_request = Soap("GetVersionCollection")
        soap_request.add_parameter("strlistID", list_id)
        soap_request.add_parameter("strlistItemID", item_id)
        soap_request.add_parameter("strFieldName", field_name)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("GetVersionCollection"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        # fix invalid attribute name: Sharepoints uses the field name as it is,
        # including whitespaces and special characters, as attribute name
        # for the Version element. To enable successful parsing, we replace
        # the attribute name (which we know anyway) by a constant, e.g. field_name
        content = response.text
        content = content.replace("Version {field_name}=\"".format(field_name=field_name), "Version field_name=\"")

        envelope = etree.fromstring(content.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        versions = envelope[0][0][0][0]
        data = []
        for row in versions.getchildren():
            data.append({
                'content': row.attrib['field_name'],
                'modified': row.attrib['Modified'],
                'editor': row.attrib['Editor']})
        return data

    def update_list_items(self, data, kind, mutate_data=False):  # type: (List[Dict[str, str]], str) -> Any
        """Update List Items
           kind = 'New', 'Update', or 'Delete'

           New:
           Provide data like so:
               data = [{'Title': 'New Title', 'Col1': 'New Value'}]

           Update:
           Provide data like so:
               data = [{'ID': 23, 'Title': 'Updated Title'},
                       {'ID': 28, 'Col1': 'Updated Value'}]

           Delete:
           Just provided a list of ID's
               data = [23, 28]
        """
        if type(data) != list:
            raise Exception("data must be a list of dictionaries")
        # Build Request
        soap_request = Soap("UpdateListItems")
        soap_request.add_parameter("listName", self.list_name)
        if kind != "Delete":
            if mutate_data:
                spdata = data
                self._mutate_to_internal(spdata)
            else:
                spdata = self._convert_to_internal(data)
        else:
            spdata = data

        soap_request.add_actions(spdata, kind)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("UpdateListItems"),
                        data=str(soap_request).encode("utf-8"),
                        verify=self._verify_ssl,
                        timeout=self.timeout)

        # Parse Response
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        # TODO: Fix me
        results = envelope[0][0][0][0]
        data_out = {}  # type: Dict
        for result in results:
            if result.text != "0x00000000" and result[0].text != "0x00000000":
                data_out[result.attrib["ID"]] = (result[0].text, result[1].text)
            else:
                data_out[result.attrib["ID"]] = result[0].text
        return data_out

    def get_attachment_collection(self, _id):  # type: (str) -> Any
        """Get Attachments for given List Item ID"""

        # Build Request
        soap_request = Soap("GetAttachmentCollection")
        soap_request.add_parameter("listName", self.list_name)
        soap_request.add_parameter("listItemID", _id)
        self.last_request = str(soap_request)

        # Send Request
        response = post(self._session,
                        url=self._url("Lists"),
                        headers=self._headers("GetAttachmentCollection"),
                        data=str(soap_request).encode("utf-8"),
                        verify=False,
                        timeout=self.timeout)

        # Parse Request
        envelope = etree.fromstring(response.text.encode("utf-8"),
                                    parser=etree.XMLParser(huge_tree=self.huge_tree,
                                    recover=True))
        # TODO: Fix this
        attaches = envelope[0][0][0][0]
        attachments = []
        for attachment in attaches.getchildren():
            attachments.append(attachment.text)
        return attachments

    # Legacy API
    GetList = get_list
    GetListItems = get_list_items
    GetView = get_view
    GetViewCollection = get_view_collection
    GetAttachmentCollection = get_attachment_collection
    UpdateListItems = update_list_items


class _List365(_List2007):
    def __init__(self,
                 session,  # type: requests.Session
                 list_name,  # type: str
                 url,  # type: Callable[[str], str]
                 verify_ssl,  # type: bool
                 users,  # type: Optional[Dict]
                 huge_tree,  # type: bool
                 timeout,  # type: Optional[int]
                 exclude_hidden_fields=False,  # type: bool
                 site_url=None):
        super().__init__(session, list_name, url, verify_ssl, users, huge_tree, timeout, exclude_hidden_fields, site_url)
        self.site_url = site_url
        self.schema = self._get_schema()
        self.version = "v365"

    def _get_schema(self):
        url = self.site_url + f"/_api/lists/getbytitle('{self.list_name}')/RenderListDataAsStream"

        body = json.dumps({"parameters": {"RenderOptions": 4}})

        headers = {'Accept': 'application/json;odata=verbose',
                   'Content-Type': 'application/json;odata=verbose',
                   'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = post(self._session, url=url, headers=headers, data=body, timeout=self.timeout)
        return response.json()

    @property
    def contextinfo(self):
        response = post(self._session, self.site_url + "/_api/contextinfo")
        data = json.loads(response.text)
        return data

    @property
    def info(self):
        return self.GetList()

    # @property
    # def views(self):
    #     return self.GetViewCollection()

    def create_field(self, title, field_type=2, required="false", unique="false", static_name=None):
        update_data = {}
        update_data['__metadata'] = {'type': 'SP.Field'}
        update_data['Title'] = title
        update_data['FieldTypeKind'] = field_type
        update_data['Required'] = required
        update_data['EnforceUniqueValues'] = unique
        update_data['StaticName'] = static_name
        body = json.dumps(update_data)

        url = self.site_url + f"/_api/lists/getbytitle('{self.list_name}')/Fields"

        headers = {'Accept': 'application/json;odata=verbose',
                   'Content-Type': 'application/json;odata=verbose',
                   'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = post(self._session, url=url, headers=headers, data=body, timeout=self.timeout)
        return response.json()
