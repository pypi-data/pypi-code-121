import re
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
from pybtex.database.input import BaseParser
from pybtex.database import Entry, Person
import csv
from warnings import warn

data_dir = Path(__file__).parent/"data"

@dataclass
class NBIBField:
    """ A field in a NBIB file. """
    code: str
    value: str


class NBIBParser(BaseParser):
    """
    Parser for NBIB/Medline/PubMed citation files.

    For information, see:
        https://www.nlm.nih.gov/bsd/policy/cit_format.html
        https://www.nlm.nih.gov/bsd/mms/medlineelements.html
    """
    default_suffix = '.nbib'
    unicode_io = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nbib_type_to_bibtex = {}

        with open(data_dir/"types.csv") as f:
            reader = csv.reader(f, delimiter=',')
            
            #skip the header
            next(reader, None)

            for row in reader:
                nbib_type = row[0]
                bibtex_type = row[1]
                self.nbib_type_to_bibtex[nbib_type] = bibtex_type

    def parse_stream(self, stream):
        text = stream.read()
        return self.parse_string(text)

    def process_entry(self, entry_text):
        # Read file into list and merge multi-line entries
        nbib_fields = []
        for line in entry_text.split('\n'):
            m = re.match(r"^([A-Z]{2,4})\s*-\s*(.*)$", line.strip())
            if m:
                code = m.group(1)
                value = m.group(2).strip()
                nbib_fields.append( NBIBField(code=code, value=value) )
            elif len(nbib_fields) > 0:
                # If the line doesn't match the pattern then append the text to the previous field
                nbib_fields[-1].value += line.strip()
            else:
                warn(f"First line of NBIB file '{line}' is invalid.")
                continue

        # Parse nbib fields
        nbib_dict = defaultdict(list)
        for field in nbib_fields:
            nbib_dict[field.code].append(field.value)

        # Get publication type
        nbib_publication_types = nbib_dict.pop("PT", [])
        bibtex_types = {
            self.nbib_type_to_bibtex[nbib_type] 
            for nbib_type in nbib_publication_types 
            if nbib_type in self.nbib_type_to_bibtex
        }
        bibtex_type = bibtex_types.pop() if len(bibtex_types) == 1 else "misc"
        nbib_publication_description = "; ".join(nbib_publication_types)

        # Create Entry object
        entry = Entry(bibtex_type)
        if nbib_publication_description:
            entry.fields["type"] = nbib_publication_description
        
        # Read People
        def add_person(code, role):
            names = nbib_dict.pop(code, [])
            for name in names:
                person = Person(name)
                entry.add_person(person, role)

        add_person("FAU", "author")
        add_person("FED", "editor")     
        # what should be done for AU and ED?   

        # Read Other Fields
        def add_field(code, bibtex_field, delimiter="; "):
            values = nbib_dict.pop(code, [])
            for value in values:
                if bibtex_field in entry.fields:
                    entry.fields[bibtex_field] += f"{delimiter}{value}"
                else:
                    entry.fields[bibtex_field] = value

        add_field("TI", "title")
        add_field("JT", "journal")
        add_field("JTI", "shortjournal")
        add_field("DP", "date")
            
        add_field("BTI", "booktitle")
        add_field("PB", "publisher")
        add_field("CY", "address")
        add_field("VI", "volume")
        add_field("PG", "pages")
        add_field("OT", "keywords", delimiter=" | ")
        add_field("GN", "note", delimiter=" | ")
        add_field("ISBN", "isbn")
        add_field("IS", "issn")
        add_field("AB", "abstract")

        add_field("AB", "abstract")

        # Read year from date field if possible
        if "date" in entry.fields:
            m = re.match(r"^(\d{4})($|\D)", entry.fields['date'])
            if m:
                entry.fields['year'] = m.group(1)

        # Get DOI
        values = nbib_dict.pop("AID", [])
        for value in values:
            if "[doi]" in value:
                entry.fields["doi"] = value.replace("[doi]", "").strip()
            else:
                nbib_dict["AID"].append(value)

        # Add the remaining fields with the RIS code as the field name
        for code, values in nbib_dict.items():
            entry.fields[code] = "; ".join(values)

        # Create an entry key if not found
        entry_key = ""
        if not entry_key:
            people = [x[0] for x in entry.persons.values()]
            if people:
                first_author = people[0]
                entry_key = "-".join(first_author.last_names).replace(" ", ".")
            elif "title" in entry.fields:
                TRUNCATE_TITLE = 20
                entry_key = entry.fields["title"].replace(" ", ".")[:TRUNCATE_TITLE]
            else:
                entry_key = "Unknown"

            if "year" in entry.fields:
                entry_key += entry.fields["year"]

        return entry_key,entry

    def parse_string(self, text):
        self.unnamed_entry_counter = 1
        self.command_start = 0

        entry_texts = re.split(r"ER\s+-", text)
        entries = (self.process_entry(t) for t in entry_texts if t.strip())
        self.data.add_entries(entries)
        return self.data



