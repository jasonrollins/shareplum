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
        else:
            print('You must pass the relative folder url to delete a folder')
        
        return None
    
    @property
    def items(self):        
        response = self._session.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/ListItemAllFields")
        data = json.loads(response.text)
        return data
    
    @property
    def files(self):        
        response = self._session.get(self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/files")
        data = json.loads(response.text)
        return data['value']
    
    def upload_file(self, content, file_name):
        body = content
        url = self.site_url + f"/_api/web/GetFolderByServerRelativeUrl('{self.folder_name}')/Files/add(url='{file_name}',overwrite=true)"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}
        
        response = self._session.post(url=url,
                                      headers=headers,
                                      data=body,
                                      timeout=self.timeout)
        
    def check_out(self, file_name): 
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/CheckOut()"
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers)
        
        return None
    
    def check_in(self, file_name, comment):
        url = self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/CheckIn(comment='{comment}',checkintype=0)"
    
        headers = {'X-RequestDigest': self.contextinfo['FormDigestValue']}

        response = self._session.post(url=url,
                                      headers=headers)
        
        return None
    
    def get_file(self, file_name):
        response = self._session.get(self.site_url + f"/_api/web/GetFileByServerRelativeUrl('{self.info['d']['ServerRelativeUrl']}/{file_name}')/$value")
        return response.text