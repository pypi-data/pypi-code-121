from kolibri.preprocess.text.cleaning.cleaning_scripts import fix_formating
from kolibri.tokenizers import SentenceTokenizer
import regex as re
from kolibri.data.text.resources import resources
from pathlib import Path
from kdmt.file import read_json_file



def _compile_patterns_in_dictionary(dictionary):
    """
    Replace all strings in dictionary with compiled
    version of themselves and return dictionary.
    """
    for name, regex_str in dictionary.items():

        if isinstance(regex_str, str):
            dictionary[name] = re.compile(regex_str, re.IGNORECASE|re.UNICODE)
        elif isinstance(regex_str, list):
            for i, reg_str in enumerate(regex_str):
                dictionary[name+'_'+str(i)] = re.compile(reg_str, re.IGNORECASE|re.UNICODE)
        elif isinstance(regex_str, dict):
            _compile_patterns_in_dictionary(regex_str)
    return dictionary


class IntentExpression():
    def __init__(self, intents='generic.json'):
        patterns_file = resources.get(str(Path('modules', 'intents', intents))).path
        self.patterns = read_json_file(patterns_file)

        self.intent_patterns = {}

        self.tokenize = SentenceTokenizer({'multi-line': False})

        for (lang, regex_set) in self.patterns.items():
            self.intent_patterns[lang] = {}
            for (name, regex_variable) in regex_set.items():
                if isinstance(regex_variable, str):
                    # The regex variable is a string, compile it and put it in the
                    # global scope
                    self.intent_patterns[lang][name] = re.compile(regex_variable, re.IGNORECASE | re.UNICODE)
                elif isinstance(regex_variable, list):
                    self.intent_patterns[lang][name] = []
                    for reg in regex_variable:
                        self.intent_patterns[lang][name].append(re.compile(reg, re.IGNORECASE | re.UNICODE))
                elif isinstance(regex_variable, dict):
                    # The regex variable is a dictionary, convert all regex strings
                    # in the dictionary to their compiled versions and put the variable
                    # in the global scope
                    self.intent_patterns[lang][name] = _compile_patterns_in_dictionary(regex_variable)
    def get_match(self, regexes, test_str):
        if test_str is None:
            return None
        intent_analysis={}
        details_intent = {}

        for regex in regexes:
            dict_name=regex.groupindex
            matches = re.finditer(regex, test_str)


            intent_analysis = {}

            for counter,match in enumerate(matches):
                for i in dict_name:
                    details= match.group(dict_name[i])
                    if details!="":
                        details_intent[i] = details


                intent_analysis['full intent'] = test_str
                intent_analysis['details'] = details_intent

                return intent_analysis

        return intent_analysis


    def _get_intent(self, patterns_, sentence):
        if len(patterns_) > 0:
            pattern=next(iter(patterns_))
            intent = self.get_match(patterns_[pattern], sentence)
            if intent:
                intent['pattern']=pattern
                return intent
            else:
                return self. _get_intent({k: v  for k, v in list(patterns_.items())[1:]}, sentence)

    def get_intent_expression(self, text, language):
        return self.__get_intent_expression(text, self.intent_patterns[language])


    def __get_intent_expression(self, text, regexes):

        sentences=self.tokenize.tokenize(fix_formating(text))

        core_intent=[]

        for sent in sentences:

            intent=self._get_intent(regexes, sent)


            if intent:
                intent["sentence"] = sent

                core_intent.append(intent)

        return core_intent
