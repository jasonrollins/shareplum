from typing import Optional

import requests
from lxml import etree

# import defusedxml.ElementTree as etree


class Office365:
    """
    Class to authenticate Office  365 Sharepoint
    """

    def __init__(self, share_point_site: str, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.share_point_site = share_point_site

    def get_security_token(self, username: str, password: str) -> Optional[str]:
        """
        Grabs a security Token to authenticate to Office 365 services
        """
        url = "https://login.microsoftonline.com/extSTS.srf"
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
            </s:Envelope>""" % (
            username,
            password,
            self.share_point_site,
        )
        headers = {"accept": "application/json;odata=verbose"}

        response = requests.post(url, body, headers=headers)

        xmldoc = etree.fromstring(response.content)

        token = xmldoc.find(
            ".//{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}BinarySecurityToken"
        )
        if token is not None:
            return token.text
        else:
            raise Exception("Check username/password and rootsite")

    def get_cookies(self) -> requests.cookies.RequestsCookieJar:
        """
        Grabs the cookies form your Office Sharepoint site
        and uses it as Authentication for the rest of the calls
        """
        sectoken = self.get_security_token(self.username, self.password)
        url = self.share_point_site + "/_forms/default.aspx?wa=wsignin1.0"
        response = requests.post(url, data=sectoken)
        return response.cookies

    # Legacy API
    GetSecurityToken = get_security_token
    GetCookies = get_cookies
