from abc import ABCMeta, abstractmethod
from typing import Iterator

import regex as re
import phonenumbers
from .fact import Fact


class ParseResult:
    def __init__(self, value, span):
        self.value = value
        self.span = span


    def to_fact(self, fact_type, doc_path):
        return Fact(
            source="mlp",
            fact_type=fact_type,
            fact_value=self.value,
            doc_path=doc_path,
            spans=[self.span]
        )


class AbstractParser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self) -> Iterator[ParseResult]:
        raise NotImplemented


class ContactPhoneParserHighRecall:
    #High Recall. Gets most of the phone numbers, output has a lot of noisy data.
    #a bit email-specific

    def __init__(self, input_text, months):
        self.text = input_text
        self.months = months


    def parse(self):
        """
        Finds all the phone numbers.
        Arguments:
        text -- A string of text to parse phone numbers from.
        Returns:
        numbers -- A list containing the numbers found.
        """
        months = self.months  # ?\:?[0-9]{2}( ?:[0-9]{2}){0,2} (GMT)?\+[0-9]{2} ?\:? ?[0-9]{2})
        pattern = re.compile(r'(?<![0-9]{2}[\./][0-9]{2}[\./])(?<![0-9]{2} [\./] [0-9]{2} [\./] )(?<!Date: )(?<!Date : )(?:\b|\+|\+\s)\d{1,4}(\s\(\s[0-9]+\s\)\s?)?[ -]?\(?\d{2,4}\)?(?:[ -]?\d{1,4}?\b)+(\s\([0-9]+\))?(?! ?:? ?[0-9]{2}( ?: ?[0-9]{2}){0,2} (GMT)?\+[0-9]{2} ?\:? ?[0-9]{2})')
        for numb in pattern.finditer(self.text):
            match_string = numb.group(0)
            if len(match_string) > 5:
                not_a_date = True
                for month in months:
                    if re.search("[0-9]{1,2} ?" + month + "\.? ?$", self.text[:numb.span()[0]].lower()) or re.search(month + " ?\.?\s[0-9]{1,2} ?\,? ?" + "$", self.text[:numb.span()[0]].lower()):
                        not_a_date = False
                        break
                if not_a_date:
                    replaced = match_string.replace(' ', '').replace('-', '').replace('+', '').replace(')', '').replace('(', '')
                    yield ParseResult(value=replaced, span=numb.span())

class ContactPhoneParserHighPrecision:
    #the output is mainly phone numbers. Excludes more complicated versions.
    def __init__(self, input_text):
        self.text = input_text

    def parse(self):
        """
        Finds all the phone numbers.
        Arguments:
        text -- A string of text to parse phone numbers from.
        Returns:
        numbers -- A list containing the numbers found.
        """
        pattern = re.compile(r'(?<![0-9a-zA-Z\:_&=\/#%@$&;])[+]*[-\s0-9]{0,4}[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s0-9]*(?![0-9a-zA-Z\:_&=\/#%@$&;])')
        for numb in pattern.finditer(self.text):
            match_string = numb.group(0).strip()
            if len(re.sub("[^0-9]", "", match_string)) > 6 and not re.search("\n", match_string):
                replaced = match_string.replace(' ', '').replace('-', '').replace('+', '')
                yield ParseResult(value=replaced, span=numb.span()) 

class ContactPhoneParserStrict:
    """
    The output is phone numbers verified by phonenumbers library.
    country_code ==> list or str of the country codes, e.g. ["RU", "GB", "DE", "FI", "LV", "LT", "SE"] #Russia, Great Britannia, Germany, Finland, Latvia, Lithuania, Sweden]
    input_text ==> text from where the numbers are parsed out
    number ==> the number to be checked by library phonenumbers

    Notes:
    if country_code is wrong, it changes that (NB! in case the nr has suunakood, otherwise it's no good...)
    Also, with sentence "Maksekorraldusele märkida viitenumber 2800049900 ning selgitus .", the "2800049900" is a valid nr in "GB", but not with "EE" or "RU". So be careful when adding country_codes!

    """
    def __init__(self, input_text, country_code=["EE", "RU"]):
        self.text = input_text
        self.country_code = country_code
        
    def valid_and_possible(self, number):

        try:
            if type(self.country_code) == str:
                nr = phonenumbers.parse(number, self.country_code)
                if phonenumbers.is_valid_number(nr): #it’s in an assigned exchange and has the right number of digits
                    return True
            else: #country_code is a list 
                for code in self.country_code:
                    nr = phonenumbers.parse(number, code)
                    if phonenumbers.is_valid_number(nr):
                        return True
        except:
            return False
        return False

    def parse(self):
        """
        Finds all the phone numbers.
        Arguments:
        text -- A string of text to parse phone numbers from.
        Returns:
        numbers -- A list containing the numbers found.
        """
        pattern = re.compile(r'(?<![0-9a-zA-Z])[+]*[-\s0-9]{0,4}[(]{0,1}[\s0-9]{1,5}[)]{0,1}[-\s0-9]*(?![0-9a-zA-Z])')
        for numb in pattern.finditer(self.text):
            match_string = numb.group(0).strip()
            if len(re.sub("[^0-9]", "", match_string)) > 6 and not re.search("\n", match_string):
                if self.valid_and_possible(match_string):
                    yield ParseResult(value=match_string.replace(' ', '').replace('-', '').replace('+', ''), span=numb.span())  

class ContactEmailParser(AbstractParser):
    def __init__(self, input_text):
        self.text = input_text


    def parse(self):
        """
        Finds all the emails in the text.
        Arguments:
        text -- A string of text containing text to parse emails from.
        Returns:
        emails -- a list containing the emails found.
        """
        pattern = re.compile(r'([^\s]+\s?\.\s?)?[^\s@]+\s?@\s?[^@.\s]+\s?[.]\s?[^\s]{1,20}')
        for email in pattern.finditer(self.text):
            yield ParseResult(value=email.group(0).replace('mailto:', '').replace(' ', ''), span=email.span())


class ContactEmailNamePairParser(AbstractParser):
    def __init__(self, input_text):
        self.text = input_text


    def parse(self):
        """
        Finds all the emails in the text.
        Arguments:
        text -- A string of text containing text to parse emails from.
        Returns:
        emails -- a list containing the emails found.
        """
        pattern = re.compile(r'(?<=(\s|:|"|^))\p{L}+\s\p{L}+"?\s(< )?([^\s]+\s?\.\s?)?[^\s@]+\s?@\s?[^@.\s]+\s?[.]\s?[^\s]{1,20}')
        for email in pattern.finditer(self.text):
            email_splitted = email.group(0).split(" ")
            if len(email_splitted[1]) > 2 and len(email_splitted[0]) > 2 and email_splitted[0].title() == email_splitted[0] and email_splitted[1].title() == email_splitted[1]:
                yield ParseResult(value=email.group(0), span=email.span())


class AddressParser(AbstractParser):
    def __init__(self, text, stanza_entities, language):
        self.text = text
        self.stanza_entities = stanza_entities
        self.language = language


    @staticmethod
    def reescape(text):
        """
        https://stackoverflow.com/questions/43662474/reversing-pythons-re-escape 
        """
        return re.sub(r'\\(.)', r'\1', text)


    @property
    def _text_with_entity_types(self):
        """
        Joins entity words with their entity type/tag, e.g input 'Peeter läks Tallinnasse' outputs to 'Peeter_PER läks Tallinnasse_LOC'
        """
        replaced_text = self.text
        # sort stanza entities and check if they actually exist in text
        ents_to_replace = [(ent, len(ent.text)) for ent in self.stanza_entities if ent.text in self.text]
        for ent in sorted(ents_to_replace, key=lambda l: l[1]):
            ent = ent[0]
            tokens = ent.text.split(' ')
            modified_ent = '{}_{}'.format('_'.join(tokens), ent.type)
            # holy shit this is ugly, but it works...
            replaced_text = replaced_text.replace(" " + ent.text + " ", " " + modified_ent + " ")
        return replaced_text


    def _parse_ru(self):
        pattern = re.compile(
            r'(?:\b)([^\s]+_LOC\s?,?\s?((д\.|дом)\s?)?\s?[0-9]+\s?([а-яА-Я]|\s?/\s?[0-9]+|-[а-я])?)[\s\n,.]')
        for addr in pattern.finditer(self._text_with_entity_types):
            value = addr.group(1).replace('_LOC', '').replace('_', ' ')
            match = re.search(re.escape(value), self.text)
            if not match:
                try:
                    match = re.search(".".join(value.split()), self.text)
                    yield ParseResult(value=value.strip(), span=match.span())
                except:
                    continue
            else:
                yield ParseResult(value=value.strip(), span=match.span())


    def _parse_others(self):
        """
        dummy method for English, Estonian, Arabic
        TODO: proper regular expression for matching addresses in each language, except for Estonian
        """
        pattern = re.compile(r'\s([^\s]+_LOC\s?\s?[0-9]+)(_[A-Z]+)?')
        for addr in pattern.finditer(self._text_with_entity_types):
            value = addr.group(1).replace('_LOC', '').replace('_', ' ')
            match = re.search(re.escape(value), self.text)
            if not match:
                try:
                    match = re.search(".".join(value.split()), self.text)
                    yield ParseResult(value=value.strip(), span=match.span())
                except:
                    continue
            else:
                yield ParseResult(value=value.strip(), span=match.span())


    def parse(self):
        # pattern to search potential addresses
        if self.language == 'ru':
            return self._parse_ru()
        else:
            return self._parse_others()
