from vaip.kg.client.neptune import NeptuneClient
from vaip.kg.model.oaisrm import Oaisrm
from vaip.utilities.json_helper import find_and_fill_placeholders
from datetime import datetime
from uuid import uuid4
import os

# TODO: Convert this to a unit test
client = NeptuneClient()
vaip_prefix = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.2#"
vaip = Oaisrm(vaip_prefix)
graph = Oaisrm(vaip_prefix)

root_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.2/entities/Rq9Smr3oCE8aV5I78Z4oVM"

vaip.load_rdf(os.path.join(os.path.dirname(__file__), "../../data/vaip-0.3.2.owl"))

tree_query = f"""
CONSTRUCT {{
    <{root_iri}> ?p ?so.
    ?o ?p2 ?o2
}}
WHERE
{{
    {{
        ?o ?p2 ?o2.
        FILTER EXISTS {{
            # The predicate pattern here is a property path matching "at least one of every predicate"
            # the vaip: prefix here is arbitrary and could be any predicate URI
            <{root_iri}> (rdf:|!rdf:)+ ?o
        }}
        # This extra filter removes all triples that are not NamedIndividuals (eg. our core ontology Classes, Properties etc)
        FILTER EXISTS {{
            ?o rdf:type owl:NamedIndividual
        }}
    }}
    UNION {{
        <{root_iri}> ?p ?so
    }}
}}
"""
result = vaip.kg.query(tree_query)

filled_placeholders = {
    "{{$.archive_data_output.Output.archive_file.Payload.checksum}}": "12345",
    "{{$.archive_data_output.Output.archive_file.Payload.archived_bucket}}": "ncap-archive-dev-nccf-archive",
    "{{$.archive_data_output.Output.archive_file.Payload.s3_uri}}": "s3://ncap-archive-dev-nccf-archive/OISST/oisst-avhrr-v02r01.20200401.nc",
    "{{$.archive_data_output.Output.archive_file.Payload.archived_key}}": "OISST/oisst-avhrr-v02r01.20200401.nc",
}

new_iri = graph.build_aiu(result, root_iri, "", f"-{str(uuid4())}", filled_placeholders)
print(new_iri)
graph.save_rdf("new_aiu.xml")