from .request_helper import get, post
import json


class _Folder():
    def __init__(self, session, folder_name, url, timeout=None):
        self._session = session
        self.folder_name = folder_name
        self._escaped_folder_name = self._escape_name(self.folder_name)
        self.site_url = url
        self.timeout = timeout

        #fetch all the existing folders
        response = get(session, self.site_url + "/_api/web/folders")
        existing_folders = {folder['Name'] for folder in response.json()}
        if not folder_name in existing_folders:
            #if the folder doesn't exist we create it
            self.info = self._create_folder()
        else:
            #else there is no need to create it
            response = get(session, self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{folder_name}')")
            self.info = {'d' : response.json()}
        self._escaped_relative_url = self._escape_name(self.info['d']['ServerRelativeUrl'])

    @property
    def contextinfo(self):
        response = post(self._session, self.site_url + "/_api/contextinfo")
        data = response.json()
        return data

    def _escape_name(self, name):
        return name.replace("'", "''")

    def _create_folder(self):
        update_data = {}
        update_data['__metadata'] = {'type': 'SP.Folder'}
        update_data['ServerRelativeUrl'] = self.folder_name
        body = json.dumps(update_data)

        url = self.site_url + f"/_api/web/folders"

        headers = {'Accept': 'application/json;odata=verbose',
                   'Content-Type': 'application/json;odata=verbose',
                   'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = post(self._session, url=url, headers=headers, data=body, timeout=self.timeout)

        return response.json()

    def delete_folder(self, relative_url):
        if relative_url == self.folder_name:
            url = self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self._escaped_folder_name}')"

            headers = {'Accept': 'application/json;odata=verbose',
                       'If-Match': '*',
                       'X-HTTP-Method': 'DELETE',
                       'Content-Type': 'application/json;odata=verbose',
                       'X-RequestDigest': self.contextinfo['FormDigestValue']}

            post(self._session, url=url, headers=headers)
        else:
            print('You must pass the relative folder url to delete a folder')

    def delete_file(self, file_name):
        escaped_file_name = self._escape_name(file_name)
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self._escaped_relative_url}/{escaped_file_name}')"

        headers = {'Accept': 'application/json;odata=verbose',
                   'If-Match': '*',
                   'X-HTTP-Method': 'DELETE',
                   'Content-Type': 'application/json;odata=verbose',
                   'X-RequestDigest': self.contextinfo['FormDigestValue']}

        post(self._session, url=url, headers=headers)

    @property
    def items(self):
        response = get(self._session, self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self._escaped_folder_name}')/ListItemAllFields")
        return response.json()

    @property
    def files(self):
        response = get(self._session, self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self._escaped_folder_name}')/files")
        return response.json()['value']

    @property
    def folders(self):
        response = get(self._session, self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self._escaped_folder_name}')/folders")
        return [entry['Name'] for entry in response.json()['value']]

    def upload_file(self, content, file_name):
        escaped_file_name = self._escape_name(file_name)
        url = self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self._escaped_folder_name}')/Files/add(url='{escaped_file_name}',overwrite=true)"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        post(self._session, url=url, headers=headers, data=content, timeout=self.timeout)

    def check_out(self, file_name):
        escaped_file_name = self._escape_name(file_name)
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self._escaped_relative_url}/{escaped_file_name}')/CheckOut()"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        post(self._session, url=url, headers=headers)

    def check_in(self, file_name, comment):
        escaped_file_name = self._escape_name(file_name)
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self._escaped_relative_url}/{escaped_file_name}')/CheckIn(comment='{comment}',checkintype=0)"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}
        post(self._session, url=url, headers=headers)

    def get_file(self, file_name):
        escaped_file_name = self._escape_name(file_name)
        response = get(self._session, self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self._escaped_relative_url}/{escaped_file_name}')/$value")
        return response.content
    
    def get_file_properties(self, file_name):
        file_properties= get(self._session, self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')?/$expand=ListItemAllFields")
        return file_properties.json()
