import json
from vaip.kg.build.oaisrm import Oaisrm
from vaip.kg.client.neptune import NeptuneClient

### There are 2 approaches currently for retrieving a value from the graph.
### 1. Get the SPARQL query that will retrive the config value and send that to Neptune directly.
### 2. Use the client to query Neptune for the graph, load that graph into the Oaisrm object, and then have it retrieve the config value.
###
### The motivation behind these approaches is that, for efficiency, we only need to have a subgraph that contains the
### Process Template node and all of the required nested edges to retrieve the config
 
kg_model = Oaisrm()
process_template_iri = "https://ncei.noaa.gov/ontologies/vaip/core/0.3.1/entities/#RCnL53mixVunkaLjLmWKYgO"
query = kg_model.compose_process_template_config_sparql(process_template_iri)
client = NeptuneClient()
response = client.query(query)
for bound_vars in response['content']['results']['bindings']:
    config = bound_vars['config']['value']
    break

config_json = json.loads(config)
print(json.dumps(config_json, indent=4))