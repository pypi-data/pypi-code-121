from vaip_model.build_kgvaip.Oaisrm import Oaisrm
from vaip_model.build_kgvaip.client.neptune import NeptuneClient

oais = Oaisrm()
oais.add("http://example.org/foo#A", "http://example.org/bar#A", "http://example.org/baz#A")
oais.add("http://example.org/foo#B", "http://example.org/bar#B", "http://example.org/baz#B")
oais.add("http://example.org/foo#C", "http://example.org/bar#C", "http://example.org/baz#C")

client = NeptuneClient()
resp = client.insert_from_oaisrm(oais)
print(resp['content'])

query = """SELECT ?p ?o WHERE {<http://example.org/foo#A> ?p ?o}"""
resp = client.query(query)
print(resp['content'])

resp = client.delete_from_oaisrm(oais)
print(resp['content'])

query = """SELECT ?p ?o WHERE {<http://example.org/foo#A> ?p ?o}"""
resp = client.query(query)
print(resp['content'])