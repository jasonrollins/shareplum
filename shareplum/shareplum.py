from __future__ import unicode_literals
from .version import __version__
from lxml import etree
import requests
from datetime import datetime
import re

from requests_toolbelt import SSLAdapter


class Office365(object):
    """
    Class to authenticate Office  365 Sharepoint
    """
    def __init__(self, share_point_site, username, password):
        self.Username = username
        self.Password = password
        self.share_point_site = share_point_site

    def GetSecurityToken(self, username, password):
        """
        Grabs a security Token to authenticate to Office 365 services
        """
        url = 'https://login.microsoftonline.com/extSTS.srf'
        body = """
                <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
                  xmlns:a="http://www.w3.org/2005/08/addressing"
                  xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
              <s:Header>
                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/trust/RST/Issue</a:Action>
                <a:ReplyTo>
                  <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                </a:ReplyTo>
                <a:To s:mustUnderstand="1">https://login.microsoftonline.com/extSTS.srf</a:To>
                <o:Security s:mustUnderstand="1"
                   xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                  <o:UsernameToken>
                    <o:Username>%s</o:Username>
                    <o:Password>%s</o:Password>
                  </o:UsernameToken>
                </o:Security>
              </s:Header>
              <s:Body>
                <t:RequestSecurityToken xmlns:t="http://schemas.xmlsoap.org/ws/2005/02/trust">
                  <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
                    <a:EndpointReference>
                      <a:Address>%s</a:Address>
                    </a:EndpointReference>
                  </wsp:AppliesTo>
                  <t:KeyType>http://schemas.xmlsoap.org/ws/2005/05/identity/NoProofKey</t:KeyType>
                  <t:RequestType>http://schemas.xmlsoap.org/ws/2005/02/trust/Issue</t:RequestType>
                  <t:TokenType>urn:oasis:names:tc:SAML:1.0:assertion</t:TokenType>
                </t:RequestSecurityToken>
              </s:Body>
            </s:Envelope>""" % (username, password, self.share_point_site)
        headers = {'accept': 'application/json;odata=verbose'}

        response = requests.post(url, body, headers=headers)

        xmldoc = etree.fromstring(response.content)

        token = xmldoc.find(
            './/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken'
        )
        if token is not None:
            return token.text
        else:
            raise Exception('Check username/password and rootsite')

    def GetCookies(self):
        """
        Grabs the cookies form your Office Sharepoint site
        and uses it as Authentication for the rest of the calls
        """
        sectoken = self.GetSecurityToken(self.Username, self.Password)
        url = self.share_point_site+ '/_forms/default.aspx?wa=wsignin1.0'
        response = requests.post(url, data=sectoken)
        return response.cookies


class Site(object):
    """Connect to SharePoint Site
    """

    def __init__(self, site_url, auth=None,authcookie=None, verify_ssl=True, ssl_version=None, huge_tree=False, timeout=None):
        self.site_url = site_url
        self._verify_ssl = verify_ssl

        self._session = requests.Session()
        if ssl_version is not None:
            self._session.mount('https://', SSLAdapter(ssl_version))

        self._session.headers.update({'user-agent':
                                          'shareplum/%s' % __version__})

        if authcookie is not None:
            self._session.cookies = authcookie
        else:
            self._session.auth = auth

        self.huge_tree = huge_tree

        self.timeout = timeout

        self.last_request = None

        self._services_url = {'Alerts': '/_vti_bin/Alerts.asmx',
                              'Authentication': '/_vti_bin/Authentication.asmx',
                              'Copy': '/_vti_bin/Copy.asmx',
                              'Dws': '/_vti_bin/Dws.asmx',
                              'Forms': '/_vti_bin/Forms.asmx',
                              'Imaging': '/_vti_bin/Imaging.asmx',
                              'DspSts': '/_vti_bin/DspSts.asmx',
                              'Lists': '/_vti_bin/lists.asmx',
                              'Meetings': '/_vti_bin/Meetings.asmx',
                              'People': '/_vti_bin/People.asmx',
                              'Permissions': '/_vti_bin/Permissions.asmx',
                              'SiteData': '/_vti_bin/SiteData.asmx',
                              'Sites': '/_vti_bin/Sites.asmx',
                              'Search': '/_vti_bin/Search.asmx',
                              'UserGroup': '/_vti_bin/usergroup.asmx',
                              'Versions': '/_vti_bin/Versions.asmx',
                              'Views': '/_vti_bin/Views.asmx',
                              'WebPartPages': '/_vti_bin/WebPartPages.asmx',
                              'Webs': '/_vti_bin/Webs.asmx'
                              }

        self.users = self.GetUsers()

    def _url(self, service):
        """Full SharePoint Service URL"""
        return ''.join([self.site_url, self._services_url[service]])

    def _headers(self, soapaction):
        headers = {"Content-Type": "text/xml; charset=UTF-8",
                   "SOAPAction": "http://schemas.microsoft.com/sharepoint/soap/" + soapaction}
        return headers

    # This is part of List but seems awkward under the List Method
    def AddList(self, listName, description, templateID):
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
        templateIDs = {'Announcements': '104',
                       'Contacts': '105',
                       'Custom List': '100',
                       'Custom List in Datasheet View': '120',
                       'DataSources': '110',
                       'Discussion Board': '108',
                       'Document Library': '101',
                       'Events': '106',
                       'Form Library': '115',
                       'Issues': '1100',
                       'Links': '103',
                       'Picture Library': '109',
                       'Survey': '102',
                       'Tasks': '107'}
        IDnums = [100, 101, 102, 103, 104, 105, 106,
                  107, 108, 109, 110, 115, 120, 1100]

        # Let's automatically convert the different
        # ways we can select the templateID
        if type(templateID) == int:
            templateID = str(templateID)
        elif type(templateID) == str:
            if templateID.isdigit():
                pass
            else:
                templateID = templateIDs[templateID]

        # Build Request
        soap_request = soap('AddList')
        soap_request.add_parameter('listName', listName)
        soap_request.add_parameter('description', description)
        soap_request.add_parameter('templateID', templateID)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('AddList'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Request
        print(response)
        if response == 200:
            return response.text
        else:
            return response

    def DeleteList(self, listName):
        """Delete a List with given name"""

        # Build Request
        soap_request = soap('DeleteList')
        soap_request.add_parameter('listName', listName)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('DeleteList'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Request
        if response == 200:
            return response.text
        else:
            return response

    def GetListCollection(self):
        """Returns List information for current Site"""
        # Build Request
        soap_request = soap('GetListCollection')
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('SiteData'),
                                      headers=self._headers('GetListCollection'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            result = envelope[0][0][0].text
            lists = envelope[0][0][1]
            data = []
            for _list in lists:
                _list_data = {}
                for item in _list:
                    key = item.tag.replace('{http://schemas.microsoft.com/sharepoint/soap/}', '')
                    value = item.text
                    _list_data[key] = value
                data.append(_list_data)

            return data
        else:
            return response

    def GetUsers(self, rowlimit=0):
        """Get Items from current list
           rowlimit defaulted to 0 (no limit)
        """

        # Build Request
        soap_request = soap('GetListItems')
        soap_request.add_parameter('listName', 'UserInfo')

        # Set Row Limit
        soap_request.add_parameter('rowLimit', str(rowlimit))
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('GetListItems'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            listitems = envelope[0][0][0][0][0]
            data = []
            for row in listitems:
                # Strip the 'ows_' from the beginning with key[4:]
                data.append({key[4:]: value for (key, value) in row.items() if key[4:]})

            return {'py': {i['ImnName']: i['ID'] + ';#' + i['ImnName'] for i in data},
                    'sp': {i['ID'] + ';#' + i['ImnName']: i['ImnName'] for i in data}}
        else:
            raise Exception("Can't get User Info List")

    # SharePoint Method Objects
    def List(self, listName):
        """Sharepoint Lists Web Service
           Microsoft Developer Network:
           The Lists Web service provides methods for working
           with SharePoint lists, content types, list items, and files.
        """
        return _List(self._session, listName, self._url, self._verify_ssl, self.users, self.huge_tree, self.timeout)


class _List(object):
    """Sharepoint Lists Web Service
       Microsoft Developer Network:
       The Lists Web service provides methods for working
       with SharePoint lists, content types, list items, and files.
    """

    def __init__(self, session, listName, url, verify_ssl, users, huge_tree, timeout):
        self._session = session
        self.listName = listName
        self._url = url
        self._verify_ssl = verify_ssl
        self.users = users
        self.huge_tree = huge_tree
        self.timeout = timeout

        # List Info
        self.fields = []
        self.regional_settings = {}
        self.server_settings = {}
        self.GetList()
        self.views = self.GetViewCollection()

        self._sp_cols = {i['Name']: {'name': i['DisplayName'], 'type': i['Type']} for i in self.fields}
        self._disp_cols = {i['DisplayName']: {'name': i['Name'], 'type': i['Type']} for i in self.fields}

        title_col = self._sp_cols['Title']['name']
        title_type = self._sp_cols['Title']['type']
        self._disp_cols[title_col] = {'name': 'Title', 'type': title_type}
        # This is a shorter lists that removes the problems with duplicate names for "Title"
        standard_source = 'http://schemas.microsoft.com/sharepoint/v3'
        # self._sp_cols = {i['Name']: {'name': i['DisplayName'], 'type': i['Type']} for i in self.fields \
        #                 if i['StaticName'] == 'Title' or i['SourceID'] != standard_source}
        # self._disp_cols = {i['DisplayName']: {'name': i['Name'], 'type': i['Type']} for i in self.fields \
        #                   if i['StaticName'] == 'Title' or i['SourceID'] != standard_source}
        self.last_request = None
        self.date_format = re.compile('\d+-\d+-\d+ \d+:\d+:\d+')

    def _url(self, service):
        """Full SharePoint Service URL"""
        return ''.join([self.site_url, self._services_url[service]])

    def _headers(self, soapaction):
        headers = {"Content-Type": "text/xml; charset=UTF-8",
                   "SOAPAction": "http://schemas.microsoft.com/sharepoint/soap/" + soapaction}
        return headers

    def _convert_to_internal(self, data):
        """From 'Column Title' to 'Column_x0020_Title'"""
        for _dict in data:
            keys = list(_dict.keys())[:]
            for key in keys:
                if key not in self._disp_cols:
                    raise Exception(key + ' not a column in current List.')
                _dict[self._disp_cols[key]['name']] = self._sp_type(key, _dict.pop(key))

    def _convert_to_display(self, data):
        """From 'Column_x0020_Title' to  'Column Title'"""
        for _dict in data:
            keys = list(_dict.keys())[:]
            for key in keys:
                if key not in self._sp_cols:
                    raise Exception(key + ' not a column in current List.')
                _dict[self._sp_cols[key]['name']] = self._python_type(key, _dict.pop(key))

    def _python_type(self, key, value):
        """Returns proper type from the schema"""
        try:
            field_type = self._sp_cols[key]['type']
            if field_type in ['Number', 'Currency']:
                return float(value)
            elif field_type == 'DateTime':


                # Need to remove the '123;#' from created dates, but we will do it for all dates
                # self.date_format = re.compile('\d+-\d+-\d+ \d+:\d+:\d+')
                value = self.date_format.search(value).group(0)
                
                # NOTE: I used to round this just date (7/28/2018)
                return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif field_type == 'Boolean':
                if value == '1':
                    return 'Yes'
                elif value == '0':
                    return 'No'
                else:
                    return ''
            elif field_type in ('User', 'UserMulti'):
                # Sometimes the User no longer exists or
                # has a diffrent ID number so we just remove the "123;#"
                # from the beginning of their name
                if value in self.users['sp']:
                    return self.users['sp'][value]
                elif '#' in value:
                    return value.split('#')[1]
                else:
                    return value
            else:
                return value
        except AttributeError:
            return value

    def _sp_type(self, key, value):
        """Returns proper type from the schema"""
        try:
            field_type = self._disp_cols[key]['type']
            if field_type in ['Number', 'Currency']:
                return value
            elif field_type == 'DateTime':
                return value.strftime('%Y-%m-%d %H:%M:%S')
            elif field_type == 'Boolean':
                if value == 'Yes':
                    return '1'
                elif value == 'No':
                    return '0'
                else:
                    raise Exception("%s not a valid Boolean Value, only 'Yes' or 'No'" % value)
            elif field_type == 'User':
                return self.users['py'][value]
            else:
                return value
        except AttributeError:
            return value

    def GetListItems(self, viewname=None, fields=None, query=None, rowlimit=0):
        """Get Items from current list
           rowlimit defaulted to 0 (unlimited)
        """

        # Build Request
        soap_request = soap('GetListItems')
        soap_request.add_parameter('listName', self.listName)
        # Convert Displayed View Name to View ID
        if viewname:
            soap_request.add_parameter('viewName', self.views[viewname]['Name'][1:-1])

        # Add viewFields
        if fields:
            # Convert to SharePoint Style Column Names
            for i, val in enumerate(fields):
                fields[i] = self._disp_cols[val]['name']
            viewfields = fields
            soap_request.add_view_fields(fields)
            # Check for viewname and query
            if [viewname, query] == [None, None]:
                # Add a query if the viewname and query are not provided
                # We sort by 'ID' here Ascending is the default
                soap_request.add_query({'OrderBy': ['ID']})

        elif viewname:
            viewfields = self.GetView(viewname)['fields']  ## Might be wrong
        else:
            # No fields or views provided so get everything
            viewfields = [x for x in self._sp_cols]

        # Add query
        if query:
            where = etree.Element('Where')

            parents = []
            parents.append(where)
            for i, field in enumerate(query['Where']):
                if field == 'And':
                    parents.append(etree.SubElement(parents[-1], 'And'))
                elif field == 'Or':
                    if parents[-1].tag == 'Or':
                        parents.pop()
                    parents.append(etree.SubElement(parents[-1], 'Or'))
                else:
                    _type = etree.SubElement(parents[-1], field[0])
                    field_ref = etree.SubElement(_type, 'FieldRef')
                    field_ref.set('Name', self._disp_cols[field[1]]['name'])
                    value = etree.SubElement(_type, 'Value')
                    value.set('Type', self._disp_cols[field[1]]['type'])
                    value.text = self._sp_type(field[1], field[2])
            query['Where'] = where
            soap_request.add_query(query)

        # Set Row Limit
        soap_request.add_parameter('rowLimit', str(rowlimit))
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('GetListItems'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            listitems = envelope[0][0][0][0][0]
            data = []
            for row in listitems:
                # Strip the 'ows_' from the beginning with key[4:]
                data.append({key[4:]: value for (key, value) in row.items() if key[4:] in viewfields})

            self._convert_to_display(data)

            return data
        else:
            return response

    def GetList(self):
        """Get Info on Current List
           This is run in __init__ so you don't
           have to run it again.
           Access from self.schema
        """

        # Build Request
        soap_request = soap('GetList')
        soap_request.add_parameter('listName', self.listName)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('GetList'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            _list = envelope[0][0][0][0]
            info = {key: value for (key, value) in _list.items()}
            for row in _list[0].getchildren():
                self.fields.append({key: value for (key, value) in row.items()})

            for setting in _list[1].getchildren():
                self.regional_settings[
                    setting.tag.strip('{http://schemas.microsoft.com/sharepoint/soap/}')] = setting.text

            for setting in _list[2].getchildren():
                self.server_settings[
                    setting.tag.strip('{http://schemas.microsoft.com/sharepoint/soap/}')] = setting.text
            fields = envelope[0][0][0][0][0]

        else:
            raise Exception("ERROR:", response.status_code, response.text)

    def GetView(self, viewname):
        """Get Info on View Name
        """

        # Build Request
        soap_request = soap('GetView')
        soap_request.add_parameter('listName', self.listName)

        if viewname == None:
            views = self.GetViewCollection()
            for view in views:
                if 'DefaultView' in view:
                    if views[view]['DefaultView'] == 'TRUE':
                        viewname = view
                        break

        if self.listName not in ['UserInfo', 'User Information List']:
            soap_request.add_parameter('viewName', self.views[viewname]['Name'][1:-1])
        else:
            soap_request.add_parameter('viewName', viewname)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Views'),
                                      headers=self._headers('GetView'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            view = envelope[0][0][0][0]
            info = {key: value for (key, value) in view.items()}
            fields = [x.items()[0][1] for x in view[1]]
            return {'info': info, 'fields': fields}

        else:
            raise Exception("ERROR:", response.status_code, response.text)

    def GetViewCollection(self):
        """Get Views for Current List
           This is run in __init__ so you don't
           have to run it again.
           Access from self.views
        """

        # Build Request
        soap_request = soap('GetViewCollection')
        soap_request.add_parameter('listName', self.listName)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Views'),
                                      headers=self._headers('GetViewCollection'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            views = envelope[0][0][0][0]
            data = []
            for row in views.getchildren():
                data.append({key: value for (key, value) in row.items()})
            view = {}
            for row in data:
                view[row['DisplayName']] = row
            return view

        else:
            return ("ERROR", response.status_code)

    def UpdateList(self):
        ### Todo: Complete this one
        pass

    def UpdateListItems(self, data, kind):
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
           Just provied a list of ID's
               data = [23, 28]
        """
        if type(data) != list:
            raise Exception('data must be a list of dictionaries')
        # Build Request
        soap_request = soap('UpdateListItems')
        soap_request.add_parameter('listName', self.listName)
        if kind != 'Delete':
            self._convert_to_internal(data)
        soap_request.add_actions(data, kind)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('UpdateListItems'),
                                      data=str(soap_request),
                                      verify=self._verify_ssl,
                                      timeout=self.timeout)

        # Parse Response
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            results = envelope[0][0][0][0]
            data = {}
            for result in results:
                if result.text != '0x00000000' and result[0].text != '0x00000000':
                    data[result.attrib['ID']] = (result[0].text, result[1].text)
                else:
                    data[result.attrib['ID']] = result[0].text
            return data
        else:
            return response

    def GetAttachmentCollection(self, _id):
        """Get Attachments for given List Item ID"""

        # Build Request
        soap_request = soap('GetAttachmentCollection')
        soap_request.add_parameter('listName', self.listName)
        soap_request.add_parameter('listItemID', _id)
        self.last_request = str(soap_request)

        # Send Request
        response = self._session.post(url=self._url('Lists'),
                                      headers=self._headers('GetAttachmentCollection'),
                                      data=str(soap_request),
                                      verify=False,
                                      timeout=self.timeout)

        # Parse Request
        if response.status_code == 200:
            envelope = etree.fromstring(response.text.encode('utf-8'), parser=etree.XMLParser(huge_tree=self.huge_tree))
            attaches = envelope[0][0][0][0]
            attachments = []
            for attachment in attaches.getchildren():
                attachments.append(attachment.text)
            return attachments
        else:
            return response


class soap(object):
    """A simple class for building SAOP Requests"""

    def __init__(self, command):
        self.envelope = None
        self.command = command
        self.request = None
        self.updates = None
        self.batch = None

        # HEADER GLOBALS
        SOAPENV_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
        SOAPENV = "{%s}" % SOAPENV_NAMESPACE
        ns0_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
        ns0 = "{%s}" % ns0_NAMESPACE
        ns1_NAMESPACE = "http://schemas.microsoft.com/sharepoint/soap/"
        ns1 = "{%s}" % ns1_NAMESPACE
        xsi_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
        xsi = "{%s}" % xsi_NAMESPACE
        NSMAP = {'SOAP-ENV': SOAPENV_NAMESPACE, 'ns0': ns0_NAMESPACE, 'ns1': ns1_NAMESPACE, 'xsi': xsi_NAMESPACE}

        # Create Header
        self.envelope = etree.Element(SOAPENV + "Envelope", nsmap=NSMAP)
        header = etree.SubElement(self.envelope, SOAPENV + "Header", nsmap=NSMAP)
        HEADER = etree.SubElement(self.envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body')

        # Create Command
        self.command = etree.SubElement(HEADER, '{http://schemas.microsoft.com/sharepoint/soap/}' + command)

        self.start_str = b"""<?xml version="1.0" encoding="utf-8"?>"""

    def add_parameter(self, parameter, value=None):
        sub = etree.SubElement(self.command, '{http://schemas.microsoft.com/sharepoint/soap/}' + parameter)
        if value:
            sub.text = value

    # UpdateListItems Method
    def add_actions(self, data, kind):
        if not self.updates:
            updates = etree.SubElement(self.command, '{http://schemas.microsoft.com/sharepoint/soap/}updates')
            self.batch = etree.SubElement(updates, 'Batch')
            self.batch.set('OnError', 'Return')
            self.batch.set('ListVersion', '1')

        if kind == 'Delete':
            for index, _id in enumerate(data, 1):
                method = etree.SubElement(self.batch, 'Method')
                method.set('ID', str(index))
                method.set('Cmd', kind)
                field = etree.SubElement(method, 'Field')
                field.set('Name', 'ID')
                field.text = str(_id)

        else:
            for index, row in enumerate(data, 1):
                method = etree.SubElement(self.batch, 'Method')
                method.set('ID', str(index))
                method.set('Cmd', kind)
                for key, value in row.items():
                    field = etree.SubElement(method, 'Field')
                    field.set('Name', key)
                    field.text = str(value)

    # GetListFields Method
    def add_view_fields(self, fields):
        viewFields = etree.SubElement(self.command, '{http://schemas.microsoft.com/sharepoint/soap/}viewFields')
        viewFields.set('ViewFieldsOnly', 'true')
        ViewFields = etree.SubElement(viewFields, 'ViewFields')
        for field in fields:
            view_field = etree.SubElement(ViewFields, 'FieldRef')
            view_field.set('Name', field)

    # GetListItems Method
    def add_query(self, pyquery):
        query = etree.SubElement(self.command, '{http://schemas.microsoft.com/sharepoint/soap/}query')
        Query = etree.SubElement(query, 'Query')
        if 'OrderBy' in pyquery:
            order = etree.SubElement(Query, 'OrderBy')
            for field in pyquery['OrderBy']:
                fieldref = etree.SubElement(order, 'FieldRef')
                fieldref.set('Name', field)
                if type(field) == tuple:
                    fieldref.set('Name', field[0])
                    if field[1] == 'DESCENDING':
                        fieldref.set('Ascending', 'FALSE')
                else:
                    fieldref.set('Name', field)

        if 'GroupBy' in pyquery:
            order = etree.SubElement(Query, 'GroupBy')
            for field in pyquery['GroupBy']:
                fieldref = etree.SubElement(order, 'FieldRef')
                fieldref.set('Name', field)

        if 'Where' in pyquery:
            Query.append(pyquery['Where'])

    def __repr__(self):
        return (self.start_str + etree.tostring(self.envelope)).decode('utf-8')

    def __str__(self, pretty_print=False):
        return (self.start_str + etree.tostring(self.envelope, pretty_print=True)).decode('utf-8')
