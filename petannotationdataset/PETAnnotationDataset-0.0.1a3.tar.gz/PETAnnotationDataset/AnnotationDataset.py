#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 19:41:22 2021

@author: patrizio


    Dataset Internal Structure
    dataset['name']                             name of the data-set
    dataset['documents'][doc_name]              a document
    
    dataset['documents'][doc_name]['sentences'][list(n_sent)]            store sentences and their annotations
    dataset['documents'][doc_name]['sentences'][n_sent]                  store a sentence
    
    dataset['documents'][doc_name]['sentences'][n_sent]['annotations']
    dataset['documents'][doc_name]['sentences'][n_sent]['annotations'][annotator_name] = entities # process elements type ranges
            
    dataset['documents'][doc_name]['sentences'][n_sent]['words']
    dataset['documents'][doc_name]['sentences'][n_sent]['words'][list(n_word)] store the list of word elements   
    dataset['documents'][doc_name]['sentences'][n_sent]['words'][n_word]['word']   string of the word 
    dataset['documents'][doc_name]['sentences'][n_sent]['words'][n_word]['pos']    word part-of-speech
    
    self.dataset['documents'][document_name]['entities'] = dict() # store annotations of a document as [annotator_name]{type: [n_sent][list of ranges]}
    self.dataset['documents'][document_name]['relations'] = dict() # store relations between entities
    
    dataset['documents'][doc_name]['sentences'][n_sent]['words'][n_word]['annotations']   a dict of annotation in the form 'annotator_name':'annotation_value'
    dataset['documents'][doc_name]['sentences'][n_sent]['words'][n_word]['annotations'][annotator_name] = annotation_value
    
    
    
    # dataset['documents'][doc_name]['entities'][annotator_name][list(n_sent)][annotation ranges]
    # dataset['documents'][doc_name]['relations'][annotator_name][list(n_sent)][annotation ranges]
    
    # # TO BE ADDED
    
    
    # dataset['documents'][doc_name]['sentences'][n_sent]['chunks']    
    # dataset['documents'][doc_name]['sentences'][n_sent]['pos']           - to be deleted, this information is reported in 'words'
    
    
    # dataset['documents'][doc_name]['annotation-relations'][list(n_sent)] store relation between annotations within a document.
    #                                                                      each element is a list of
    #                                                                      [
    #                                                                      source: 'n_sent-word_number' of the beginning of an annotation,
    #                                                                      relation type: a string,
    #                                                                      reference: 'n_sent-word_number' of the beginning of an annotation
    #                                                                      ]
    
    
    #  'entities', 'relations'
"""

import json

# import nltk
#
# from Utility.Tags import IS_SENTENCE, SENTENCE_TYPE, SENTENCE_AGREEMENT
# from Utility.Tags import Tags
#

# def SaveJsonData(data, filename=None):
#     try:
#         print(type(data))
#         with open(filename, 'w') as fout:
#             json.dump(data, fout)
#         return True
#     except:
#         return False
#
# def LoadJsonData(filename):
#     try:
#         with open(filename, 'r') as fin:
#             return json.load(fin)
#     except:
#         return False
# #
# class CONSTANTS:
#     PROCESS_ELEMENTS = [
#                         'Activity',
#                         'Activity Data',
#                         'Further Specification',
#                         'Condition Specification',
#                         'Actor',
#                         'XOR Gateway',
#                         'AND Gateway',
#                         ]
#
#     PROCESS_ANNOTATION_LAYERS = [
#                         'Behavioral',
#                         'Organizational',
#                         'Activity Data',
#                         'Further Specification'
#                         ]
#
#     # { layer: list of process elements}
#     # this link the theoretical layers with the annotation layers
#     PROCESS_MODEL_LAYERS = {
#                         'Behavioral': ['Activity', 'Further Specification', 'Condition Specification', 'XOR Gateway', 'AND Gateway'],
#                         'Data Object': ['Activity Data'],
#                         'Organizational': ['Actor']
#                         }

def SaveJsonData(data, filename=None):
    # try:
    # print(type(data))
    with open(filename, 'w') as fout:
        json.dump(data, fout)
    return True
    # except:
    #     return False


def LoadJsonData(filename):
    # try:
    with open(filename, 'r') as fin:
        return json.load(fin)
    # except:
    #     return False


class AnnotationDataset:
    gold_standard_annotator_name = 'Gold Standard'

    def __len__(self):
        return len(self.dataset['documents'])

    def __init__(self, name=None):
        self.__init_variables__()
        if name:
            self.dataset['name'] = name


    def __init_variables__(self):
        self.dataset = {'name': 'empty dataset',
                        'documents':{}}

    def SaveDataset(self, filename):
        return SaveJsonData(data=self.dataset,
                            filename=filename)
    def LoadDataset(self, filename):
        data = LoadJsonData(filename=filename)
        if data:
            self.dataset = data
            return True
        else:
            self.__init_variables__()
            return False

    def AddDocument(self, document_name: str, sentences:list):
        """
        

        Parameters
        ----------
        document_name : str
            name of the document.
        sentences : list
            a list of sentences words.

        Returns
        -------
        None.

        """
        # check if document exist. if so, do not add any document
        if document_name in list(self.dataset['documents'].keys()):
            return

        self.dataset['documents'][document_name] = dict()
        self.dataset['documents'][document_name]['sentences'] = list()
        self.dataset['documents'][document_name]['entities'] = dict()
        self.dataset['documents'][document_name]['relations'] = dict()
        self.dataset['documents'][document_name]['entities-relaxed'] = dict()
        self.dataset['documents'][document_name]['relations-relaxed'] = dict()

        for sentence in sentences:
            sentence_dict = {'annotations':dict(),
                             'words': list(),
                             'chunks': list(),
                             'pos': list(),
                             }
            # posses = nltk.pos_tag(sentence)
            # for n_w, witem in enumerate(zip(sentence, posses)):
            #     w, pos = witem
            #     pos = pos[1]
            #     # Words
            #     sentence_dict['words'].append({'word':w, 'pos':pos, 'annotations':dict()})
            # posses = nltk.pos_tag(sentence)
            for n_w, w in enumerate(sentence):
                sentence_dict['words'].append({'word': w, 'pos': None, 'annotations': dict()})
            # add chunks

            self.dataset['documents'][document_name]['sentences'].append(sentence_dict)

    def GetEntities(self,
                    document_name,
                    annotator_name,
                    ):

        return self.dataset['documents'][document_name]['entities'][annotator_name]

    def GetGoldStandardEntities(self,
                                document_name):
        return self.dataset['documents'][document_name][self.gold_standard_annotator_name]['entities']

# DEV
    def GetPredictedEntities(self,
                                document_name,
                             predictor_name):
        return self.dataset['documents'][document_name]['predictors'][predictor_name]['entities']

    def GetRelations(self,
                     document_name,
                     annotator_name,
                     ):

        return self.dataset['documents'][document_name]['relations'][annotator_name]

    def GetEntitiesRelaxed(self,
                           document_name,
                           annotator_name,
                           ):

        return self.dataset['documents'][document_name]['entities-relaxed'][annotator_name]

    def GetGoldStandardRelations(self,document_name):
        return self.dataset['documents'][document_name][self.gold_standard_annotator_name]['relations']

    def GetRelationsRelaxed(self,
                            document_name,
                            annotator_name,
                            ):

        return self.dataset['documents'][document_name]['relations-relaxed'][annotator_name]


    def AddRelaxedAnnotations(self,
                              document_name,
                              annotator_name,
                              entities_relaxed,
                              relations_relaxed,
                              ):
        self.dataset['documents'][document_name]['entities-relaxed'][annotator_name] = entities_relaxed
        self.dataset['documents'][document_name]['relations-relaxed'][annotator_name] = relations_relaxed

    def _annotation_exist(self,
                          doc_name,
                          annotator_name):
        try:
            if annotator_name in list(self.dataset['documents'][doc_name]['sentences'][0]['words'][0]['annotations'].keys()):
                return True
            return False
        except:
            return False

    def AddTokenAnnotation(self,
                           document_name,
                           annotator_name,
                           annotation_data,
                           entities,
                           relations,
                           update_existing_annotation=False):
        """
        
            annotation data is a list of  (annotation values, annotation index)
            
            entities store the annotation ranges for each annotator_name for each process element type
        """
        # check if the annotaion exist
        if self._annotation_exist(document_name, annotator_name) and not update_existing_annotation:
            print('Annotations for ', document_name, 'of the user ', annotator_name, 'already exist')
            print('You must set update_existing_annotation to True if you want to update them')
            return

        for sent_number, sent_annotation in enumerate(annotation_data):
            for n_word, witem in enumerate(sent_annotation):
                word, annotation  = witem
                self.dataset['documents'][document_name]['sentences'][sent_number]['words'][n_word]['annotations'][annotator_name] = annotation

        self.dataset['documents'][document_name]['entities'][annotator_name] = entities
        self.dataset['documents'][document_name]['relations'][annotator_name] = relations

    def AddRelationsAnnotation(self, document_name,
                               annotator_name,
                               relations) :
        # relations is a list of [origin, [type, reference]]

        self.dataset['documents'][document_name]['annotation-relations'] = relations

    def AddPredictedTokenAnnotation(self,
                           document_name,
                           annotator_name,
                           entities):
        """

            annotation data is a list of  (annotation values, annotation index)

            entities store the annotation ranges for each annotator_name for each process element type
        """
        # check if the annotaion exist
        if 'predictors' in self.dataset['documents'][document_name].keys():
            if annotator_name in self.dataset['documents'][document_name]['predictors'].keys():
                self.dataset['documents'][document_name]['predictors'][annotator_name]['entities'] = entities
            else:
                self.dataset['documents'][document_name]['predictors'][annotator_name] = {'relations': None,
                                                                                          'entities': entities}
        else:
            self.dataset['documents'][document_name]['predictors'] = {annotator_name: {'entities': entities}}

    def AddPredictedRelationsAnnotation(self,
                                        document_name,
                                        annotator_name,
                                        relations):
        # relations is a list of [origin, [type, reference]]
        if 'predictors' in self.dataset['documents'][document_name].keys():
            if annotator_name in self.dataset['documents'][document_name]['predictors'].keys():
                self.dataset['documents'][document_name]['predictors'][annotator_name]['relations'] = relations
            else:
                self.dataset['documents'][document_name]['predictors'][annotator_name] = {'relations': relations,
                                                                                          'entities' : None}
        else:
            self.dataset['documents'][document_name]['predictors'] =  {annotator_name: {'relations': relations}}

    # =============================================================================
    # # SENTENCE       
    # =============================================================================
    def GetSentenceText(self,
                        document_name: str,
                        sentence_number: int):
        text = ''
        for n_word, word in enumerate(self.dataset['documents'][document_name]['sentences'][sentence_number]['words']):
            text = '{} {}'.format(text, word['word'])
        return text

    def GetSentenceListOfWords(self,
                               document_name: str,
                               sentence_number: int):
        text = list()
        for n_word, word in enumerate(self.dataset['documents'][document_name]['sentences'][sentence_number]['words']):
            text.append(word['word'])
        return text

    def GetDocuments(self):
        return sorted(list(self.dataset['documents'].keys()))

    def GetGoldStandardDocuments(self):
        documents = sorted([doc_name for doc_name in self.dataset['documents'].keys()
                            if self.gold_standard_annotator_name in self.dataset['documents'][doc_name]
                            ])
        return documents

    def GetAnnotatorDocuments(self, annotator_name):
        print('TODO GetAnnotatorDocuments')
        assert False
    def GetAnnotatorDocumentEntities(self, doc_name, annotator_name):
        print('TODO GetAnnotatorDocumentEntities')
        assert False

    def GetAnnotatorDocumentRelations(self, doc_name, annotator_name):
        print('TODO GetAnnotatorDocumentRelations')
        assert False

    def GetNWords(self, doc_name, n_sent):
        return len(self.dataset['documents'][doc_name]['sentences'][n_sent]['words'])

    def GetNSentences(self, doc_name):
        return len(self.dataset['documents'][doc_name]['sentences'])

    def GetWordAnnotations(self,
                           doc_name: str,
                           n_sent: int,
                           n_word: int,
                           annotator_list: list):

        return [self.dataset['documents'][doc_name]['sentences'][n_sent]['words'][n_word]['annotations'][annotator_name]
                for annotator_name in annotator_list]


    # def GetWordAgreement(self,
    #                      doc_name: str,
    #                      n_sent: int,
    #                      n_word: int,
    #                      annotator_list: list):
    #     """
    #         Get a dict of float with the percentual agreement on the item
    # 
    #         return
    #     """
    #     # self.dataset
    # 
    #     annotations = self.GetWordAnnotations(doc_name, n_sent, n_word, annotator_list)
    #     annotations_tmp_dict = {annotations.count(k): k for k in set(annotations)}
    #     scores = {v:k  for k, v in annotations_tmp_dict.items()}
    #     try:
    #         max_annotation_count = max(list(annotations_tmp_dict))
    #         max_agreement_type = annotations_tmp_dict[max_annotation_count]
    #         try:
    #             agreement = max_annotation_count/len(annotator_list)
    #         except ZeroDivisionError:
    #             agreement = 0
    # 
    #         return max_agreement_type, max_annotation_count, agreement, scores
    #     except ValueError:
    #         #  ValueError: max() arg is an empty sequence
    #         return '-', 0, 0, {}