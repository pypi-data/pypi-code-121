from vaip.kg.client.neptune import NeptuneClient
from vaip.kg.model.oaisrm import Oaisrm
from uuid import uuid4

client = NeptuneClient()
new_graph = Oaisrm()

root_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.2/entities/Rq9Smr3oCE8aV5I78Z4oVM"
graph_name = "http://brandon.ncei.noaa.gov/vaip/0.3.2"

query = client.retrieve_deep_node_tree(root_iri, graph_name)
response = client.query(query)
rows = response['content']

iri_id_prefix = ""
iri_id_suffix = f"-{str(uuid4())}"
new_graph.copy_query_results_to_new_graph(rows, iri_id_prefix, iri_id_suffix)
new_graph.save_rdf("copied.xml")