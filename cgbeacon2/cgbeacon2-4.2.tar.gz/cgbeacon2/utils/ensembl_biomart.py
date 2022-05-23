"""Code for downloading all genes with coordinates from Ensembl Biomart"""
import logging

import requests

BIOMART_37 = "http://grch37.ensembl.org/biomart/martservice?query="
BIOMART_38 = "http://ensembl.org/biomart/martservice?query="
CHROMOSOMES = [str(num) for num in range(1, 23)] + ["X", "Y", "MT"]
ATTRIBUTES = [
    "chromosome_name",
    "start_position",
    "end_position",
    "ensembl_gene_id",
    "hgnc_symbol",
    "hgnc_id",
]

LOG = logging.getLogger(__name__)


class EnsemblBiomartClient:
    """Class to handle requests to the ensembl biomart api"""

    def __init__(self, build="GRCh37") -> None:
        """Initialise a ensembl biomart client"""
        self.server = BIOMART_37
        if build == "GRCh38":
            self.server = BIOMART_38
        self.filters = {"chromosome_name": CHROMOSOMES}
        self.attributes = [
            "ensembl_gene_id",
            "hgnc_id",
            "hgnc_symbol",
            "chromosome_name",
            "start_position",
            "end_position",
        ]
        self.xml = self._create_biomart_xml()
        self.header = True

    def _create_biomart_xml(self) -> str:
        """Convert biomart query params into biomart xml query

        Accepts:
            filters(dict): keys are filter names and values are filter values
            attributes(list): a list of attributes

        Returns:
            xml: a query xml file

        """
        filter_lines = self._xml_filters()
        attribute_lines = self._xml_attributes()
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<!DOCTYPE Query>",
            '<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows'
            ' = "0" count = "" datasetConfigVersion = "0.6" completionStamp = "1">',
            "",
            '\t<Dataset name = "hsapiens_gene_ensembl" interface = "default" >',
        ]
        for line in filter_lines:
            xml_lines.append("\t\t" + line)
        for line in attribute_lines:
            xml_lines.append("\t\t" + line)
        xml_lines += ["\t</Dataset>", "</Query>"]

        return "\n".join(xml_lines)

    def _xml_filters(self) -> list:
        """Creates a filter line for the biomart xml document

        Returns:
            formatted_lines(list[str]): List of formatted xml filter lines
        """
        formatted_lines = []
        for filter_name in self.filters:
            value = self.filters[filter_name]
            if isinstance(value, str):
                formatted_lines.append(
                    '<Filter name = "{0}" value = "{1}"/>'.format(filter_name, value)
                )
            else:
                formatted_lines.append(
                    '<Filter name = "{0}" value = "{1}"/>'.format(filter_name, ",".join(value))
                )

        return formatted_lines

    def _xml_attributes(self) -> list:
        """Creates an attribute line for the biomart xml document

        Returns:
            formatted_lines(list(str)): list of formatted xml attribute lines
        """
        formatted_lines = []
        for attr in self.attributes:
            formatted_lines.append('<Attribute name = "{}" />'.format(attr))
        return formatted_lines

    def query_service(self):
        """Query the Ensembl biomart service and yield the resulting lines
        Accepts:
            xml(str): an xml formatted query, as described here:
                https://grch37.ensembl.org/info/data/biomart/biomart_perl_api.html

        Yields:
            biomartline
        """
        url = "".join([self.server, self.xml])
        try:
            with requests.get(url, stream=True) as r:
                for line in r.iter_lines():
                    yield line.decode("utf-8")
        except Exception as ex:
            LOG.info("Error downloading data from biomart: {}".format(ex))
            return
