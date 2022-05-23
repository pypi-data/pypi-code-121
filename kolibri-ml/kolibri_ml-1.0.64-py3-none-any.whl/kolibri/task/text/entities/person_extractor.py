from kolibri.tokenizers.kolibri_tokenizer import KolibriTokenizer
from kolibri.core.entity import Entity
from kolibri.task.text.entities.dictionaryExtractor import DictionaryExtractor
import re

from kolibri.data.text.resources import resources
from pathlib import Path


person_file_name = resources.get(str(Path('corpora', 'gazetteers', 'default','first_name.txt'))).path

class PersonExtractor(DictionaryExtractor):
    def __init__(self, case_sensitive=False):
        DictionaryExtractor.__init__(self, person_file_name, 'Person', case_sensitive=case_sensitive)
        self.tokenizer = KolibriTokenizer(configs={"outout-type": "tokens"})

    def get_entities(self, text):
        #    print(d)
        tokens = self.tokenizer.tokenize(text)

        persons = self.keywords.extract_keywords(text, True)

        # print(persons)

        FinalPersonns = []
        j = 0
        for person in persons:
            for i in range(j, len(tokens)):
                if tokens[i].text==person[0]:
                    if  tokens[i].get('type') in ['CANDIDATE', 'ACRONYM']:
                        FinalPersonns.append(Entity(self.type, tokens[i].text, tokens[i].start, tokens[i].end))
                    elif i < len(tokens) - 1 and tokens[i + 1].get('type') in ['CANDIDATE', 'ACRONYM']:
                        FinalPersonns.append(
                            Entity(self.type, tokens[i].text + ' ' + tokens[i + 1].text, tokens[i].start,
                                   tokens[i + 1].end))
                    j = i + 1
        employeeids = []

        for person in FinalPersonns:
            person.value = re.sub(r"^(Hi|Hello|Dear|However|If|Employees?)\s", '', person.value)
            person.start = person.end - len(person.value)
            person.value = re.sub(r"'s$", '', person.value)
            person.end = person.start + len(person.value)
            pattern = re.escape(
                person.value) + r"[\s\(\[#]*(?P<EmployeeId>e?\d{4,8}\b)|\b(?P<EmployeeId2>e?\d{4,8}\b)[\s\)\]#]*" + re.escape(
                person.value)
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                for group, index in zip(match.groups(), range(0, len(match.group()))):
                    if group is not None:
                        employeeids.append(
                            Entity("EmployeeId", group, match.start(index + 1), match.end(index + 1)))

                # print(match.groups())
                # for groupidx in range(0, len(match.group())):
                #     if match.group(groupidx) is not None:
                #         employeeids.append(Entity("EmployeeId", match.group(groupidx), match.start(groupidx), match.end(groupidx)))

        FinalPersonns.extend(employeeids)
        return FinalPersonns


if __name__ == '__main__':
    text = """I'm trying to update my Workday profile and it's unclear how to accurately enter in past companies I've worked for. It won't recognize Takeda or Astellas. I get an error message and there's no directory."""
    pe = PersonExtractor(False)

    entities = pe.get_entities(text)

    for e in entities:
        print(e.tojson())
