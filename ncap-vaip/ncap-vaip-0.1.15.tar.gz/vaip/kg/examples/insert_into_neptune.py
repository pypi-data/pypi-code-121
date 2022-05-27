from vaip_model.build_kgvaip.client.neptune import NeptuneClient

client = NeptuneClient()

insert = """INSERT DATA { 
        <http://example.org/foo#A> <http://example.org/bar#A> <http://example.org/baz#A>.
        <http://example.org/foo#B> <http://example.org/bar#B> <http://example.org/baz#B>.
        <http://example.org/foo#C> <http://example.org/bar#C> <http://example.org/baz#C>.
        }"""

delete = """DELETE DATA { 
        <http://example.org/foo#A> <http://example.org/bar#A> <http://example.org/baz#A>.
        <http://example.org/foo#B> <http://example.org/bar#B> <http://example.org/baz#B>.
        <http://example.org/foo#C> <http://example.org/bar#C> <http://example.org/baz#C>.
        }"""

query = """SELECT ?p ?o WHERE {<http://example.org/foo#A> ?p ?o}"""

resp = client.update(insert)
print(resp['content'])

resp = client.query(query)
print(resp['content'])

resp = client.update(delete)
print(resp['content'])

resp = client.query(query)
print(resp['content'])
