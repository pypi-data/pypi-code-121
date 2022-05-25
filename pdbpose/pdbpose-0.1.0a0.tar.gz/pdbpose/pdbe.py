from typing import Iterable, Tuple
from requests import post


def chains(uniprot: str) -> Iterable[Tuple[str, str]]:
    url = "https://www.ebi.ac.uk/pdbe/search/pdb/select?"
    query = f"uniprot_accession:{uniprot} AND status:REL"
    filter_list = "pdb_id,struct_asym_id"
    data = {"q": query, "fl": filter_list, "rows": 1000000, "wt": "json"}
    response = post(url, data=data, timeout=30)
    response.raise_for_status()
    for doc in response.json().get("response", {}).get("docs", []):
        for asym_id in doc["struct_asym_id"]:
            yield doc["pdb_id"], asym_id
