# -*- coding: utf8 -*-
import json
from typing import List, Optional

import regex as re


class EntityMapper:

    def __init__(self, entity_data: dict):
        """
        :param entity_data: Dictionary where the key constitutes the label and the value a path to the JSON file containing the values.
        """
        self.entities, self.longest_entity = self._load_entities(entity_data)
        self.entity_map = self._create_entity_map()


    def _create_entity_map(self):
        """
        Takes the entities and creates an entity_map

        Returns:
        entity_map -- A dictionary with entities as keys and type as the value of the key
        """
        entity_map = {}
        for entity_type, entity_list in self.entities.items():
            for entity in entity_list:
                if entity not in entity_map:
                    entity_map[entity] = entity_type
        return entity_map


    def _load_entities(self, entity_files: dict):
        """
        Loads entities from a file into a dict and stores the length of the longest entity.

        Arguments:
        entity_data -- a list that contains the type and location of the entities, for example: [('addr', 'addresses.txt')]

        Returns:
        entities -- A dict with the entity type and its contents  

        longest_entity -- the longest entity from all the entities
        """

        entities = {}
        longest_entity = 0

        for entity_file in entity_files:
            with open(entity_file, encoding='utf8') as fh:
                try:
                    # Try to read as json
                    for label, values in json.loads(fh.read()).items():
                        values = [self._normalize_string(value) for value in values]
                        if label not in entities:
                            entities[label] = {}

                        for w in values:
                            entities[label][w] = True

                        entity_len = max([len(w.split(' ')) for w in values])
                        if entity_len > longest_entity:
                            longest_entity = entity_len

                except:
                    # If fails, read as txt file
                    entities[entity_file] = {}
                    for values in fh.readlines():
                        values = self._normalize_string(values)
                        entities[entity_file][values] = True

                        entity_len = len(values.split(' '))
                        if entity_len > longest_entity:
                            longest_entity = entity_len

        return entities, longest_entity


    @staticmethod
    def _normalize_string(entity: str):
        """
        Takes in an argument string 'entity' and returns it after lowering it and stripping whitespace
        """
        entity = entity.lower().strip()
        return entity


    def map_entities(self, text: str, doc_path='', entity_types: Optional[List] = None):
        """
        Maps entities in given text.

        Arguments:
        text -- A string of text to map. For example: u'I live on Street 1, not Street 2'

        doc_path='' -- Path to the given document where the text was taken from.        


        Returns:
        filtered_mappings -- A sorted (descending by value length) dict that has redundant matches removed.
        For example: {'addr': [{'span': (57, 69), 'doc_path': '', 'value': u'Street 2'}, {'span': (41, 51), 'doc_path': '', 'value': u'Street 1'}]}
        """
        if not entity_types:
            entity_types = list(self.entities.keys())

        mappings = []

        text = self._normalize_string(text)

        for n in range(1, self.longest_entity + 1):
            ngrams = self._ngrams(text, n)
            for ngram in ngrams:
                ngram = ' '.join(ngram)
                # This is kinda hacky, but it kinda fixes Stanza tokenization errors.
                ngram = ngram.replace(".", "").strip()
                # Checks if ngram is in the entity map. If so, define its type and add it to the mappings
                if ngram in self.entity_map:
                    entity_type = self.entity_map[ngram]
                    if entity_type in entity_types:
                        mapping = {'entity_type': entity_type, 'entity': ngram}
                        if mapping not in mappings:
                            mappings.append(mapping)
        mappings_dict = {}
        for mapping in mappings:
            if mapping['entity_type'] not in mappings_dict:
                mappings_dict[mapping['entity_type']] = []
            mappings_dict[mapping['entity_type']].append({'value': mapping['entity']})

        mappings = self._add_spans(mappings_dict, text, doc_path)
        mappings = self._remove_redundant_matches(mappings)

        return mappings


    @staticmethod
    def _remove_redundant_matches(mappings: dict):
        """
        Takes in the mappings of entities and removes redundant matches.

        Arguments: 
        mappings -- A dict that contains the facts about the entities, including the span, doc_path, type and value.
        For example: {'addr': [{'span': (41, 51), 'doc_path': '', 'value': u'Street 1'}, {'span': (57, 69), 'doc_path': '', 'value': u'Street 2'}]}

        Returns:
        filtered_mappings -- A sorted (descending by value length) dict that has redundant matches removed.
        For example: {'addr': [{'span': (57, 69), 'doc_path': '', 'value': u'Street 2'}, {'span': (41, 51), 'doc_path': '', 'value': u'Street 1'}]}
        """
        filtered_mappings = {}

        for entity_type in mappings.keys():
            filtered_matches = []
            # Sorts by the length of the values in the entity type in descending order.
            sorted_matches = sorted(
                mappings[entity_type], key=lambda k: len(k['value']), reverse=True)

            for match in sorted_matches:
                m_start = match['span'][0]
                m_end = match['span'][1]
                redundant = False

                for filtered_match in filtered_matches:
                    fm_start = filtered_match['span'][0]
                    fm_end = filtered_match['span'][1]

                    if m_start >= fm_start and m_end <= fm_end:
                        redundant = True
                        break

                if redundant == False:
                    filtered_matches.append(match)

            filtered_mappings[entity_type] = filtered_matches

        return filtered_mappings


    @staticmethod
    def _add_spans(mappings: dict, text: str, doc_path: str):
        """
        Adds spans (character number locations of entities) and the document path to the entity dict.

        Arguments:
        mappings -- A dict that contains entity types, and the values of different entities under that type.
        For example: {'addr': [{'value': u'Street 1'}, {'value': u'Street 2'}]}

        text -- The input text given for mapping

        doc_path -- Path to the doc containing the entity

        Returns:
        facts -- A dict that contains the facts about the entities, including the span, doc_path, type and value.
        For example: {'addr': [{'span': (41, 51), 'doc_path': '', 'value': u'Street 1'}, {'span': (57, 69), 'doc_path': '', 'value': u'Street 2'}]}
        """
        facts = {}

        for entity_type in mappings.keys():
            values_with_spans = []
            for entity in mappings[entity_type]:
                # get entity value, like u'Street 1' and compile a regex pattern
                pattern = re.compile(entity['value'])
                for match in pattern.finditer(text):
                    value_with_span = {'value': entity['value']}
                    value_with_span['span'] = (match.start(), match.end())
                    if doc_path:
                        value_with_span['doc_path'] = doc_path
                    values_with_spans.append(value_with_span)

            if entity_type not in facts:
                facts[entity_type] = []
            facts[entity_type] = values_with_spans
        return facts


    @staticmethod
    def _ngrams(inp: str, n: int):
        """
        Takes in an input text and returns ngrams

        Arguments: 
        inp -- Input text

        n -- The range of iteration

        Returns:
        returns a list that contains words as tuples, the word count depends on the argument 'n',
        for example if n is 1, the output will contain only one word per list value, ex: ([(u'example',), (u'string',), (u'here',)])
        but if n is 2, the output will contain two words per list value, ex: ([(u'example string',), (u'string here',))])
        """
        if type(inp) in [bytes, str]:
            inp = inp.split(' ')
        return zip(*[inp[i:] for i in range(n)])


if __name__ == '__main__':
    entity_data = {'addr': 'data/addresses.txt'}
    em = EntityMapper(entity_data)
    print(em.map_entities(
        u'Selles stringis on aadressid, milleks on Ülikooli 2 ning Kentmanni 13'))
