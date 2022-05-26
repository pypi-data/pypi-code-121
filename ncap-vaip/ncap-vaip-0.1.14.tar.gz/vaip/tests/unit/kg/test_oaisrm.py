import os
import unittest
from pathlib import Path
from pyshacl import validate

import vaip.data
from vaip.kg.model.oaisrm import Oaisrm


class OaisrmTest(unittest.TestCase):

    def setUp(self):
        path = Path(vaip.data.__file__)
        owl_dir = path.parent.absolute()
        self.rdf_file = os.path.join(owl_dir, 'vaip-0.3.1.owl')

        bucket = "nccf-ncap-archive"
        key = "archive/oisst/oisst-avhrr-v02r01.343.nc"
        s3_uri = f"s3://{bucket}/{key}"

        aiu1_dict = {
            "uuid": "a152455f-3547-451f-9796-82a9867466ae",
            "bucket": bucket,
            "key": key,
            "s3_uri": s3_uri,
            "checksum": "23a6498ef444dcde36efb400a3a1",
            "algorithm": "SHA-256",
            "size": 1337,
            "dateTime": "2021-04-01T00:00:00Z"
        }
        key = "archive/oisst/oisst-avhrr-v02r01.251.nc"
        s3_uri = f"s3://{bucket}/{key}"
        aiu2_dict = {
            "uuid": "11acb5b4-5ee2-4d70-bade-d4f133231962",
            "bucket": bucket,
            "key": key,
            "s3_uri": s3_uri,
            "checksum": "ac467f1515f2535a472ff631217a2497",
            "algorithm": "SHA-512",
            "size": 89037,
            "dateTime": "2019-10-11T00:00:00Z"
        }
        key = "archive/oisst/oisst-avhrr-v02r01.196.nc"
        s3_uri = f"s3://{bucket}/{key}"
        aiu3_dict = {
            "uuid": "c558f4c9-266d-4825-b8b3-6fdc28403a08",
            "bucket": bucket,
            "key": key,
            "s3_uri": s3_uri,
            "checksum": "ec935a9d7c03ac87c0a05a4f045a8d9d",
            "algorithm": "MD5",
            "size": 149061,
            "dateTime": "2017-02-16T10:00:00Z"
        }
        self.aiu_list = [aiu1_dict, aiu2_dict, aiu3_dict]
        # self.build_granules(aiu_list, 3)
        # Serialize
        # print("\n============================== Graph RDF ==============================")
        # print(self.oaisrm.kg.serialize(format='xml', indent=4))

    def test_validate_graph(self):
        conforms, v_graph, v_text = validate(self.rdf_file, data_graph_format='xml', inference='rdfs', debug=True,
                                             serialize_report_graph=True)
        print(v_text)
        self.assertTrue(conforms, "Graph is non-conforming.")

    def test_query_has_bits(self):
        oaisrm = Oaisrm("https://ncei.noaa.gov/ontologies/vaip/core/0.3.2#")
        kg = oaisrm.load_rdf(self.rdf_file)
        sparql = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX vaip: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.1#>
            SELECT ?aiu ?bits 
            WHERE {
                ?aiu vaip:hasBits ?bits .
            }
            """

        print("\n============================== Query Results ==============================")
        bit_cnt = 0
        for row in kg.query(sparql):
            bit_cnt = bit_cnt + 1
            bits = row["bits"]
            aiu = row["aiu"]
            print(f"{aiu} has bits {bits}")

        assert bit_cnt >= 21


    # def test_build_granules(self):
    #     oaisrm = Oaisrm()
    #     sparql_client = NeptuneClient()
    #     i = 1
    #     for aiu_item in self.aiu_list:
    #         oaisrm.build_granule(sparql_client, aiu_item["uuid"], aiu_item["key"], aiu_item["s3_uri"], aiu_item["size"],
    #                                   aiu_item["checksum"], aiu_item["algorithm"], aiu_item["dateTime"])
    #         if i < 3:
    #             i = i + 1
    #             continue
    #         break

    # def test_build_granule(self):
    #     sparql_client = NeptuneClient()
    #     self.oaisrm = Oaisrm()
    #     uuid = str(uuid4())
    #     storage_template_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.1/entities/#RCVIb9IdKicBBVLVhUSJIxN"
    #     rdf = self.oaisrm.build_granule(sparql_client, storage_template_iri, uuid, "ncap-archive-dev",
    #                                     "archive/oisst/oisst-avhrr-v02r01.196.nc",
    #                                     "s3://ncap-archive-dev/archive/oisst/oisst-avhrr-v02r01.196.nc",
    #                                     "23a6498ef444dcde36efb400a3a1")
    #     print(rdf)
    #     return

    #
    # def test_return_aiu_values(self):
    #
    #     # Use url base owl for graph initialization
    #     self.oaisrm = Oaisrm()
    #     owl_iri = "https://ncap-archive-dev-pub.s3.us-east-1.amazonaws.com/vaip/vaip.owl"
    #     self.oaisrm.load_rdf(owl_iri)
    #     storage_template_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.0/entities/#RCVIb9IdKicBBVLVhUSJIxN"
    #
    #     print("\n============================== Find AIU Results ==============================")
    #     sparql_prefix = """
    #         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         PREFIX owl: <http://www.w3.org/2002/07/owl#>
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    #         PREFIX core: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.0#>
    #         """
    #     sparql_select = "SELECT ?s ?p ?o ?data ?bits ?label\n"
    #     constraint = "WHERE { \n"\
    #                  f" <{storage_template_iri}> ?p ?o .\n" \
    #                  "  ?o core:hasDataObject ?data .\n" \
    #                  "  ?data core:hasBits ?bits .\n" \
    #                  "  ?data rdfs:label ?label \n" \
    #                  "}"
    #     sparql = sparql_prefix + sparql_select + constraint
    #     print(sparql)
    #
    #
    #     template_values = self.oaisrm.kg.query(sparql)
    #     file_link = ""
    #     for row in template_values:
    #         label = row["label"]
    #         bits = row["bits"]
    #         print(f"{label}: {bits}")
    #         if f"{label}" == "File Link":
    #             file_link = bits
    #
    #     assert str(file_link) == "{{FILE LINK}}"
    #
    # def test_query_has_bits_checksum_filter(self):
    #     oaisrm = Oaisrm()
    #     kg = oaisrm.load_rdf(self.rdf_file)
    #
    #     sparql = """
    #         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         PREFIX owl: <http://www.w3.org/2002/07/owl#>
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    #         PREFIX vaip: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.1#>
    #         SELECT ?aiu ?bits ?label
    #         WHERE {
    #             ?aiu vaip:hasBits ?bits .
    #             ?aiu rdf:label ?label .
    #             FILTER(?label="*Checksum*")
    #         }
    #         """
    #
    #     print("\n============================== Query Results hasBits with checksum filter ===========================")
    #     bit_cnt = 0
    #
    #     for row in kg.query(sparql):
    #         bit_cnt = bit_cnt + 1
    #         bits = row["bits"]
    #         aiu = row["aiu"]
    #         print(f"{aiu} has bits {bits}")
    #
    #     # Should return 3 checksum values
    #     assert bit_cnt >= 3
    #
    # def test_query_has_bits_uuid_filter(self):
    #     oaisrm = Oaisrm()
    #     kg = oaisrm.load_rdf(self.rdf_file)
    #
    #     sparql = """
    #         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         PREFIX owl: <http://www.w3.org/2002/07/owl#>
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    #         PREFIX vaip: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.0#>
    #         SELECT ?aiu ?bits ?label
    #         WHERE {
    #             ?aiu vaip:hasBits ?bits .
    #             ?aiu rdf:label ?label .
    #             FILTER(?label="UUID")
    #         }
    #         """
    #
    #     print("\n============================== Query Results hasBits with uuid filter ==============================")
    #     bit_cnt = 0
    #     for row in kg.query(sparql):
    #         bit_cnt = bit_cnt + 1
    #         bits = row["bits"]
    #         aiu = row["aiu"]
    #         print(f"{aiu} has bits uuid {bits}")
    #
    #     # Should return 3 uuid values
    #     assert bit_cnt == 3
    #
    # def test_query_has_bits_filter_by_uuid(self):
    #     bits = None
    #     oaisrm = Oaisrm()
    #     kg = oaisrm.load_rdf(self.rdf_file)
    #
    #     sparql = """
    #         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         PREFIX owl: <http://www.w3.org/2002/07/owl#>
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    #         PREFIX vaip: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.0#>
    #         SELECT ?aiu ?bits ?label
    #         WHERE {
    #             ?aiu vaip:hasBits ?bits .
    #             ?aiu rdf:label ?label .
    #             FILTER(?bits="a152455f-3547-451f-9796-82a9867466ae")
    #         }
    #         """
    #
    #     print("\n============================== Query Results hasBits with uuid filter ==============================")
    #     for row in kg.query(sparql):
    #         bits = row["bits"]
    #
    #     assert f"{bits}" == "a152455f-3547-451f-9796-82a9867466ae"
    #
    # def test_query_has_bits_date_filter(self):
    #     oaisrm = Oaisrm()
    #     kg = oaisrm.load_rdf(self.rdf_file)
    #     sparql = """
    #         PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #         PREFIX owl: <http://www.w3.org/2002/07/owl#>
    #         PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    #         PREFIX vaip: <https://ncei.noaa.gov/ontologies/vaip/core/0.3.0#>
    #         SELECT ?aiu ?bits ?label
    #         WHERE {
    #             ?aiu vaip:hasBits ?bits .
    #             ?aiu rdf:label ?label .
    #             FILTER(?label="File DateTime")
    #         }
    #         """
    #
    #     print("\n============================== Query Results hasBits with date filter ==============================")
    #     bit_cnt = 0
    #     for row in kg.query(sparql):
    #         bit_cnt = bit_cnt + 1
    #         bits = row["bits"]
    #         aiu = row["aiu"]
    #         print(f"{aiu} has bits date time {bits}")
    #
    #     # Should return 3 date_time values
    #     assert bit_cnt == 3
    #
    # def test_retrieve_template(self):
    #     oaisrm = Oaisrm()
    #     oaisrm.load_rdf(self.rdf_file)
    #     # Pass in process template uri, vaip.owl reference
    #     # Return granule or storage template
    #     process_template_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.1/entities/#R8r2pKohikKt7DSGtLZoeFI"
    #     owl_iri = "https://ncap-archive-dev-pub.s3.us-east-1.amazonaws.com/vaip/vaip.owl"
    #     template_iri = oaisrm.retrieve_template(process_template_iri, owl_iri)
    #
    #     assert str(template_iri) == "https://ncei.noaa.gov/ontologies/vaip/core/0.3.1/entities/#RCVIb9IdKicBBVLVhUSJIxN"
