from typing import Dict
from typing import List
from typing import Optional

from lxml import etree

# import defusedxml.ElementTree as etree


class Soap:
    """A simple class for building SOAP Requests"""

    def __init__(self, command: str) -> None:
        self.envelope = None
        self.command = command
        self.request = None
        self.updates = None
        self.batch = None

        # HEADER GLOBALS
        SOAPENV_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
        SOAPENV = "{%s}" % SOAPENV_NAMESPACE
        ns0_NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
        ns1_NAMESPACE = "http://schemas.microsoft.com/sharepoint/soap/"
        xsi_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
        NSMAP = {"SOAP-ENV": SOAPENV_NAMESPACE, "ns0": ns0_NAMESPACE, "ns1": ns1_NAMESPACE, "xsi": xsi_NAMESPACE}

        # Create Header
        self.envelope = etree.Element(SOAPENV + "Envelope", nsmap=NSMAP)
        HEADER = etree.SubElement(self.envelope, "{http://schemas.xmlsoap.org/soap/envelope/}Body")

        # Create Command
        self.command = etree.SubElement(HEADER, "{http://schemas.microsoft.com/sharepoint/soap/}" + command)

        self.start_str = b"""<?xml version="1.0" encoding="utf-8"?>"""

    def add_parameter(self, parameter: str, value: Optional[str] = None) -> None:
        sub = etree.SubElement(self.command, "{http://schemas.microsoft.com/sharepoint/soap/}" + parameter)
        if value:
            sub.text = value

    # UpdateListItems Method
    def add_actions(self, data: List[Dict[str, str]], kind: str) -> None:
        if not self.updates:
            updates = etree.SubElement(self.command, "{http://schemas.microsoft.com/sharepoint/soap/}updates")
            self.batch = etree.SubElement(updates, "Batch")
            if self.batch:
                self.batch.set("OnError", "Return")
                self.batch.set("ListVersion", "1")

        if kind == "Delete":
            for index, _id in enumerate(data, 1):
                method = etree.SubElement(self.batch, "Method")
                if method:
                    method.set("ID", str(index))
                    method.set("Cmd", kind)
                field = etree.SubElement(method, "Field")
                if field:
                    field.set("Name", "ID")
                    field.text = str(_id)

        else:
            for index, row in enumerate(data, 1):
                method = etree.SubElement(self.batch, "Method")
                if method:
                    method.set("ID", str(index))
                    method.set("Cmd", kind)
                for key, value in row.items():
                    field = etree.SubElement(method, "Field")
                    if field:
                        field.set("Name", key)
                        field.text = str(value)

    # GetListFields Method
    def add_view_fields(self, fields: List[str]) -> None:
        viewFields = etree.SubElement(self.command, "{http://schemas.microsoft.com/sharepoint/soap/}viewFields")
        viewFields.set("ViewFieldsOnly", "true")
        ViewFields = etree.SubElement(viewFields, "ViewFields")
        for field in fields:
            view_field = etree.SubElement(ViewFields, "FieldRef")
            view_field.set("Name", field)

    # GetListItems Method
    def add_query(self, pyquery: Dict) -> None:
        query = etree.SubElement(self.command, "{http://schemas.microsoft.com/sharepoint/soap/}query")
        Query = etree.SubElement(query, "Query")
        if "OrderBy" in pyquery:
            order = etree.SubElement(Query, "OrderBy")
            for field in pyquery["OrderBy"]:
                fieldref = etree.SubElement(order, "FieldRef")
                if type(field) == tuple:
                    fieldref.set("Name", field[0])
                    if field[1] == "DESCENDING":
                        fieldref.set("Ascending", "FALSE")
                else:
                    fieldref.set("Name", field)

        if "GroupBy" in pyquery:
            order = etree.SubElement(Query, "GroupBy")
            for field in pyquery["GroupBy"]:
                fieldref = etree.SubElement(order, "FieldRef")
                fieldref.set("Name", field)

        if "Where" in pyquery:
            Query.append(pyquery["Where"])

    def __repr__(self) -> str:
        return (self.start_str + etree.tostring(self.envelope)).decode("utf-8")

    def __str__(self, pretty_print: bool = False) -> str:
        return (self.start_str + etree.tostring(self.envelope, pretty_print=True)).decode("utf-8")
