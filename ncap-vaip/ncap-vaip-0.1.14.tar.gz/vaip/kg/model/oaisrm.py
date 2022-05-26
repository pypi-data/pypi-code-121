import rdflib
from rdflib.namespace import XSD
from vaip.utilities.rdf_helper import is_valid_uri
from vaip.utilities.json_helper import find_and_fill_placeholders


class Oaisrm:
    """
    Class use to build knowgledge graph using OAIS Reference Model an VAIP ontology.
    """
    def __init__(self, vaip_prefix):
        """
        Initialize class by constructing a base knowledge graph.
        """
        self.namespaces = {
            "vaip": rdflib.Namespace(vaip_prefix)
        }
        self.kg = self.build_vaip_knowledge_graph()
        self.vaip_prefix = vaip_prefix

    def build_vaip_knowledge_graph(self):
        kg = rdflib.Graph()
        for prefix, ns in self.namespaces.items():
            kg.namespace_manager.bind(prefix, ns)

        return kg

    def save_rdf(self, path, format="application/rdf+xml"):
        self.kg.serialize(destination=path, format=format, encoding="utf-8")

    def save_rdf_text(self, format="application/rdf+xml"):
        return self.kg.serialize(destination=None, format=format, encoding="utf-8").decode("utf-8")

    def load_rdf(self, path, format="application/rdf+xml"):
        self.kg.parse(path, format=format)
        return self.kg

    def load_rdf_text(self, data, format="application/rdf+xml"):
        self.kg.parse(data=data, format=format)
        return self.kg

    def add(self, s, p, o):
        obj = None
        if not is_valid_uri(o):
            obj = rdflib.Literal(o)
        else:
            obj = rdflib.URIRef(o)
        self.kg.add((rdflib.URIRef(s), rdflib.URIRef(p), obj))
        return self

    def copy_query_results_to_new_graph(self, rows, original_root_iri, id_prefix, id_suffix, placeholder_payload):
        """ 
        Loop through the query result rows and build a map of old_id -> new_id, where
        id in this case refers to the string segment after the final trailing slash of our IRI
        eg. http://uri.of.thing/entities/{thing_id}
    
        We then format each row as a string in n-triple format, and finally join this
        list of triples and replace all the old_ids with new_ids contained in the iri_map.
        """
        self.kg = self.build_vaip_knowledge_graph()

        iri_map = {}
        new_triples = []
        for row in rows:
            subject = row[0]
            predicate = row[1]
            obj = row[2]
            subj_prefix, subj_id = subject.rsplit("/", 1)
            if subject not in iri_map:
                new_id = f"{id_prefix}{subj_id}{id_suffix}"
                iri_map[str(subject)] = f"{subj_prefix}/{new_id}"

            new_obj = None
            if isinstance(obj, rdflib.URIRef):
                new_obj = f"<{str(obj)}>"
            elif isinstance(obj, rdflib.Literal):
                str_obj = str(obj)
                if (str_obj.startswith("{{") and str_obj.endswith("}}")):
                    if str_obj in placeholder_payload:
                        new_obj = f'"{placeholder_payload[str_obj]}"'
                    else:
                        new_obj = f'"{str_obj}"'
                else:
                    new_obj = f'"{str_obj}"'
            new_triples.append(f"<{str(subject)}> <{str(predicate)}> {new_obj} .")
        
        nt_triples = "\n".join(new_triples)
        for k, v in iri_map.items():
            nt_triples = nt_triples.replace(k, v)
        
        self.load_rdf_text(data=nt_triples, format="nt")
        return iri_map[original_root_iri]

    def build_and_add_new_aic_member(self, member_template_rows, member_template_iri, member_container_iri, id_prefix, id_suffix, placeholder_payload):
        new_member_iri = self.copy_query_results_to_new_graph(member_template_rows, member_template_iri, id_prefix, id_suffix, placeholder_payload)

        self.kg.add((rdflib.URIRef(member_container_iri), self.namespaces['vaip'].hasDataObject, rdflib.URIRef(new_member_iri)))
        return new_member_iri

    def build_aiu(self, rows, original_root_iri, id_prefix, id_suffix, placeholder_payload):
        # Clone it
        new_root_iri = self.copy_query_results_to_new_graph(rows, original_root_iri, id_prefix, id_suffix, placeholder_payload)

        return new_root_iri
