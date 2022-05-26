import json
from uuid import uuid4
from vaip_model.build_kgvaip.Oaisrm import Oaisrm
from vaip_model.build_kgvaip.client.neptune import NeptuneClient

bucket = "nccf-ncap-archive"
key = "archive/oisst/oisst-avhrr-v02r01.343.nc"
s3_uri = f"s3://{bucket}/{key}"

client = NeptuneClient()
kg = Oaisrm()
storage_template_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.0/entities/Rq9Smr3oCE8aV5I78Z4oVM"
graph_name = "http://brandon.ncei.noaa.gov/vaip/0.3.1"

for i in range(5):
    aiu = {
        "uuid": str(uuid4()),
        "bucket": bucket,
        "key": key,
        "s3_uri": s3_uri,
        "checksum": "23a6498ef444dcde36efb400a3a1",
    }

    aiu_iri = kg.build_granule(client, storage_template_iri, aiu['uuid'], aiu['bucket'], aiu['key'], aiu['s3_uri'], aiu['checksum'])
    kg.save_rdf(f"/home/brandon.shelton/AIU-{i}.xml")
    print(kg.save_rdf_text())
    insert = client.insert_from_oaisrm(kg, graph_name)

    # validate = f"""
    # SELECT ?s ?p ?o
    # WHERE {{
    #    BIND (<{aiu_iri}> as ?s)
    #    GRAPH <{graph_name}>
    #    {{ ?s ?p ?o }}
    # }}
    # """
    # query_resp = client.query(validate)
    # delete = client.delete_from_oaisrm(kg, graph_name)
    # for result in query_resp['content']:
    #    print(result)