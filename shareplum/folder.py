import requests
import json

class _Folder():
    def __init__(self, session, folder_name, url):
        self._session = session
        self.folder_name = folder_name
        self.site_url = url
        self.timeout = 3

        self.info = self._create_folder()

    @property
    def contextinfo(self):
        response = self._session.post(self.site_url + "/_api/contextinfo")
        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        data = json.loads(response.text)
        return data

    def _create_folder(self):
        update_data = {}
        update_data['__metadata'] = {'type': 'SP.Folder'}
        update_data['ServerRelativeUrl'] = self.folder_name
        body = json.dumps(update_data)

        url = self.site_url + f"/_api/web/folders"

        headers = {'Accept': 'application/json;odata=verbose',
                   'Content-Type': 'application/json;odata=verbose',
                   'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers,
                                      data=body,
                                      timeout=self.timeout)

        if response.status_code not in [200, 201]:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        data = json.loads(response.text)
        return data

    def delete_folder(self, relative_url):
        if relative_url == self.folder_name:
            url = self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')"

            headers = {'Accept': 'application/json;odata=verbose',
                       'If-Match': '*',
                       'X-HTTP-Method': 'DELETE',
                       'Content-Type': 'application/json;odata=verbose',
                       'X-RequestDigest': self.contextinfo['FormDigestValue']}

            response = self._session.post(url=url,
                                          headers=headers)

            if response.status_code != 200:
                response.raise_for_status()
                raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))
        else:
            print('You must pass the relative folder url to delete a folder')

        return None

    def delete_file(self, file_name):
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')"

        headers = {'Accept': 'application/json;odata=verbose',
                    'If-Match': '*',
                    'X-HTTP-Method': 'DELETE',
                    'Content-Type': 'application/json;odata=verbose',
                    'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                        headers=headers)

        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        return None

    @property
    def items(self):
        response = self._session.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/ListItemAllFields")
        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        data = json.loads(response.text)
        return data

    @property
    def files(self):
        response = self._session.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/files")
        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        data = json.loads(response.text)
        return data['value']

    @property
    def folders(self):
        response = self._session.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/folders")
        response.raise_for_status()
        return [entry['Name'] for entry in response.json()['value']]

    def upload_file(self, content, file_name):
        url = self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/Files/add(url='{file_name}',overwrite=true)"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers,
                                      data=content,
                                      timeout=self.timeout)

        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

    def check_out(self, file_name):
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/CheckOut()"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers)

        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        return None

    def check_in(self, file_name, comment):
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/CheckIn(comment='{comment}',checkintype=0)"

        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers)

        if response.status_code != 200:
            response.raise_for_status()
            raise RuntimeError("Response code: " + str(response.status_code) + ", response: " + str(response.text))

        return None

    def get_file(self, file_name):
        response = self._session.get(self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/$value")
        response.raise_for_status()
        return response.content
