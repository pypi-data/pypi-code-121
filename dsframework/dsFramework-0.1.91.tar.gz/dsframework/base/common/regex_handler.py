#!/usr/bin/env python
# coding: utf-8

##
# @file
# @brief This file hold all regular expressions used in the project.
#        We declare the pattern and compile them for better performance.
#        We wrap each regex / group of regexes with functions as API
#        For example RegexHandler.url2.findall(text) -> find all urls in the text
#        in the background we use
#        RegexHandler.url2 = re.compile(url_pattern2)
#        url_pattern2 = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
#
#        Another example with emojis:
#        ----------------------------
#        we define:
#        emoji_pattern = u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])'
#        emoji = re.compile(emoji_pattern, flags=re.UNICODE)
#        and then we can use:
#        emojis = RegexHandler.emoji.findall(t)  // -> in order to find emojis
#        or
#        return RegexHandler.emoji.sub(r'', t)  // -> in order to remove all emojis from text

import datetime
import math
import re
import string
import sys
import unicodedata
from string import punctuation
from unidecode import unidecode
import tldextract

class RegexHandler:
    def __init__(self):
        pass

    url_pattern = r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
    url_pattern2 = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    ## For example 36 steps , 0.1ms  (https://www.example.com/)
    url_pattern3 = r"((http|https):\/\/)(www.)?[a-zA-Z0-9@:%._\\+~#?&\/\/=]{2,256}\.[a-z]{2,6}([-a-zA-Z0-9@:%._\\+~#?&\/\/=]*)"
    email_pattern = r"([\w\.-]{1,256}@[\w\.-]{1,256}\.\w{1,256})"
    emoji_pattern = u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])'
    number_pattern = r'\d+'
    join_spaces_pattern = r' {2,}'
    join_nl_pattern = r'\n{2,}'
    html_pattern = r'<.*?>'
    time_pattern = r'^(([01]\d|2[0-3]):([0-5]\d)|24:00)$'
    has_time_pattern = r'(\d+):(\d+)'
    contact_prefixes_pattern = ['email', 'linkedin', 'twitter', 'mail']
    contact_prefixes_pattern = '(' + '|'.join(contact_prefixes_pattern) + ')[: ]+'
    connections_hyphen_pattern = r'(\d+)[\-]?(direct|office|main|fax|mob|cel)'
    tel_patterns = r'(toll\s?\-?free:|general:|general tel:|helpline:|line:|call:|main:|customer service:|general line:)\s*(\+?\d+)'
    direct_pattern = r'(direct call\:?)\s*(\+?\d+)'
    toll_free_pattern = r'toll[\s\-] free (service|tel)'
    no_number_pattern = r'(\s+)(no:|number:)(\+?\d+)'
    po_box1_pattern = r'\np\.?o\.?\s*?box\.?\s*?\:?\n(\d+)'
    po_box2_pattern = r'p\.?o\.?\s*?box\.?\s*?\:\s*(\d+)'
    follow_me_pattern = r'follow me on'
    since_pattern = r'since \d{4}'
    all_rights_pattern = r'ALL RIGHTS RESERVED'
    hours_prefix_pattern = r'(office|operating|branch|working) (hours|hrs).*(\n|$)'
    offices_pattern = r' (offices\:?\s+)'
    corporate_pattern = r'corporate (office\:?)'
    plus_phone_pattern1 = r'(\d{3,20})\/(\+\d+)'
    plus_phone_pattern2 = r'(\D+:)(\+?\d+)'
    tel_link_pattern = r'tel:([\s]?\d{3,20})'
    dot_list_pattern = r'\n(\d\.\s+)(\w+)'
    direct_line_dial_pattern = r'direct (line|dial)'
    main_line_pattern = r'(main line)|(HelpTel)'
    main_office_pattern = r'main office'
    email_prefix_pattern = r'[eE]-mail'
    skype_prefix_pattern = r'skype:'
    separator_pattern = r' by |│| • | · | I | l '
    url_junk_pattern = r'[0-9a-fA-F%/-]'
    # split_by_separator_pattern = r' *[\|~] *'
    semicolon_spaces_pattern = r'\s+(:|,)'
    digits_brackets_pattern = r'\(\s?(\+?\d+)\s?\)'
    rep_with_space_pattern = r'(\*|~|\|)'
    number_with_x_pattern = r'\bx(\d+)\b'
    concat_phones_pattern1 = r'(\d{6,20}/\d*)\s+(\d{8,20})'
    concat_phones_pattern2 = r'(\d{5,20})\s+(\d{3}-\d+\D*)'
    concat_phones_pattern3 = r'(\d{3,4}-\d{3,4})\s+(\d+-\d+)'
    concat_phones_pattern4 = r'(\d{6,20})\s+(\d{5,20})'
    ref_pattern = r'ref[\s]?\d+'

    ref = re.compile(ref_pattern)
    concat_phones1 = re.compile(concat_phones_pattern1)
    concat_phones2 = re.compile(concat_phones_pattern2)
    concat_phones3 = re.compile(concat_phones_pattern3)
    concat_phones4 = re.compile(concat_phones_pattern4)
    number_with_x = re.compile(number_with_x_pattern)
    rep_with_space = re.compile(rep_with_space_pattern)
    digits_brackets = re.compile(digits_brackets_pattern)
    semicolon_spaces = re.compile(semicolon_spaces_pattern)
    tel = re.compile(tel_patterns, flags=re.I)
    direct = re.compile(direct_pattern, flags=re.I)
    connections_hyphen = re.compile(connections_hyphen_pattern, flags=re.I)
    toll_free = re.compile(toll_free_pattern, flags=re.I)
    no_number = re.compile(no_number_pattern, flags=re.I)
    po_box1 = re.compile(po_box1_pattern, flags=re.I)
    po_box2 = re.compile(po_box2_pattern, flags=re.I)
    follow_me = re.compile(follow_me_pattern, flags=re.I)
    offices = re.compile(offices_pattern)
    since = re.compile(since_pattern, flags=re.I)
    all_rights = re.compile(all_rights_pattern, flags=re.I)
    hours_prefix = re.compile(hours_prefix_pattern, flags=re.I)
    corporate = re.compile(corporate_pattern, flags=re.I)
    plus_phone1 = re.compile(plus_phone_pattern1, flags=re.I)
    plus_phone2 = re.compile(plus_phone_pattern2, flags=re.I)
    tel_link = re.compile(tel_link_pattern)
    dot_list = re.compile(dot_list_pattern, flags=re.I)
    direct_line_dial = re.compile(direct_line_dial_pattern, flags=re.I)
    main_line = re.compile(main_line_pattern, flags=re.I)
    main_office = re.compile(main_office_pattern, flags=re.I)
    email_prefix = re.compile(email_prefix_pattern, flags=re.I)
    skype_prefix = re.compile(skype_prefix_pattern, flags=re.I)
    separator = re.compile(separator_pattern)
    url_junk = re.compile(url_junk_pattern)
    # split_by_separator = re.compile(split_by_separator_pattern)
    contact_prefixes = re.compile(contact_prefixes_pattern,flags=re.I)


    url = re.compile(url_pattern)
    url2 = re.compile(url_pattern2)
    url3 = re.compile(url_pattern3)
    email = re.compile(email_pattern)
    emoji = re.compile(emoji_pattern, flags=re.UNICODE)
    number = re.compile(number_pattern)
    merge_lines = re.compile(join_nl_pattern)
    merge_spaces = re.compile(join_spaces_pattern)
    html = re.compile(html_pattern)
    time = re.compile(time_pattern)
    has_time = re.compile(has_time_pattern)
    camelCase1 = re.compile(r'([A-Z][a-z]+)')
    camelCase2 = re.compile(r'([A-Z]+)')
    camelCase3 = re.compile(r'(.)([A-Z][a-z]+)')
    camelCase4 = re.compile(r'([a-z0-9])([A-Z])')
    camelCase5 = re.compile(r'([A-Z])_([A-Z]+[0-9]*[A-Z]+)')
    bad_decoding = re.compile(r'^(\s*=?[A-F][A-F0-9]=?\s*)+$')
    # square_brackets = re.compile(r'\[[^)^\]]*\]')
    brackets_cid = re.compile(r'\(cid:[^)]*\)')
    usd_amount = re.compile(r'\$\d{2,}\.?\d*')

    keywords = []

    word2num = {'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
                'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
                'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80,
                'ninety': 90
                }

    months = ['january', 'jan', 'february', 'feb', 'march', 'mar', 'april', 'apr']
    months += ['may', 'june', 'jun', 'july', 'jul', 'august', 'aug', 'september', 'sep', 'sept']
    months += ['october', 'oct', 'november', 'nov', 'december', 'dec']

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    days += ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    # build a table mapping all non-printable characters to None
    NOPRINT_TRANS_TABLE = {
        i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable()
    }

    @staticmethod
    def remove_ref(s):
        """
        handles cases of digits followed by one of direct|office|main|fax|mob|cel (with/without "-" between)
        it will remove the "-" if exists and separate the number and the word with a space
        @param s: string
        @return: string
        """
        new_text = []
        for l in s.split("\n"):
            if len(RegexHandler.ref.findall(l.lower())) > 0:
                continue
            else:
                new_text.append(l)
        return "\n".join(new_text)

    @staticmethod
    def sub_connections_hyphen(s):
        """
        handles cases of digits followed by one of direct|office|main|fax|mob|cel (with/without "-" between)
        it will remove the "-" if exists and separate the number and the word with a space
        @param s: string
        @return: string
        """
        return RegexHandler.connections_hyphen.sub(r'\1 \2', s)

    @staticmethod
    def sub_separators(s):
        """
        replaces different types of separators to "|"
        @param s: string
        @return: string
        """
        return RegexHandler.separator.sub(' | ', s)

    @staticmethod
    def sub_main_office(s):
        """
        Part of the text_formatter. replaces main office to "Office"
        @param s: string
        @return: string
        """
        return RegexHandler.main_office.sub('Office ', s)

    @staticmethod
    def sub_skype_email_prefix(s):
        """
         Part of the text_formatter. Replaces email/E-mail/e-mail to Email, and also all types of skype (SKYPE) to Skype
        @param s: string
        @return: string
        """
        s = RegexHandler.email_prefix.sub('Email ', s)
        return RegexHandler.skype_prefix.sub('Skype: ', s)

    @staticmethod
    def sub_direct_line_dial(s):
        """
        Part of text_formatter. Replaces Direct line/dial to "Direct "
        @param s: string
        @return: string
        """
        return RegexHandler.direct_line_dial.sub('Direct ', s)

    # noinspection PyMethodParameters
    def sub_main_line(s):
        """
        Part of text_formatter. Replaces main line to "Tel "
        @param s: string
        @return: string
        """
        return RegexHandler.main_line.sub('Tel ', str(s))

    @staticmethod
    def sub_tel_link(s):
        """
        Part of text_formatter. handles cases of <a tel:123456 />
        @param s: string
        @return: string
        """
        return RegexHandler.tel_link.sub(r' \1', s)

    @staticmethod
    def sub_dot_list(s):
        """
        Part of text_formatter. handles cases such:
        "1. text" -> " text"
        @param s: string
        @return: string
        """
        return RegexHandler.dot_list.sub(r'\n \2', s)

    @staticmethod
    def sub_plus_phone(s):
        """
        Part of text_formatter. handles cases such:
        "+12345678" -> "12345678"
        @param s: string
        @return: string
        """
        s = RegexHandler.plus_phone1.sub(r'\1 \2', s)
        return RegexHandler.plus_phone2.sub(r'\1 \2', s)

    @staticmethod
    def sub_offices_corporate(s):
        s = RegexHandler.offices.sub(r'\n \1', s)
        return RegexHandler.corporate.sub(r' \1', s)

    @staticmethod
    def sub_hours_prefix(s):
        """
        Part of text_formatter. Replaces prefix before hours (office|working|etc..) to ''
        @param s: string
        @return: string
        """
        return RegexHandler.hours_prefix.sub('', s)

    @staticmethod
    def sub_non_sig_text(s):
        """
        Part of text_formatter. Removed non relevant text (follow me on| all rights reserved | etc..)
        @param s: string
        @return: string
        """
        s = RegexHandler.follow_me.sub('', s)
        s = RegexHandler.since.sub('', s)
        return RegexHandler.all_rights.sub('', s)

    @staticmethod
    def sub_po_box(s):
        """
        Part of text_formatter. Standardized po box text to PO BOX
        @param s: string
        @return: string
        """
        s = RegexHandler.po_box1.sub(r'\nPO BOX \1', s)
        return RegexHandler.po_box2.sub(r'PO BOX \1', s)

    @staticmethod
    def sub_no_number(s):
        """
        Part of text_formatter. handles "  no:/number: 123456" -> "  123456"
        @param s: string
        @return: string
        """
        return RegexHandler.no_number.sub(r'\1 \3', s)

    @staticmethod
    def sub_patterns_2_tel(s):
        """
        Part of text_formatter. Replaces several telephone prefix to "Tel: "
        @param s: string
        @return: string
        """
        text = RegexHandler.direct.sub(r'Direct: \2', s)
        return RegexHandler.tel.sub(r'Tel:  \2', text)

    @staticmethod
    def sub_toll_free(s):
        """
        Part of text_formatter. Replaces several Toll-free  to "Toll-Free: "
        @param s: string
        @return: string
        """
        return RegexHandler.toll_free.sub(r'Toll-Free', s)

    @staticmethod
    def remove_non_printable_chars(s):
        """Replace non-printable characters in a string."""
        # the translate method on str removes characters
        # that map to None from the string
        return s.translate(RegexHandler.NOPRINT_TRANS_TABLE)

    @staticmethod
    def condense_numbers(t):
        """
        every two numbers separated by "," are condensed together
        @param t:
        @return: t
        """
        return re.sub(r'(\d+),(\d+)', r'\1\2', t)

    # @staticmethod NOT USED
    # def contain_usd_amounts(t):
    #     return len(RegexHandler.usd_amount.findall(t)) > 0

    # @staticmethod NOT USED
    # def get_usd_amounts(t):
    #     return RegexHandler.usd_amount.findall(t)

    # @staticmethod NOT USED
    # def set_keywords(t_list):
    #     if type(t_list) is not list:
    #         t_list = [t_list]
    #     RegexHandler.keywords = [t.lower() for t in t_list]

    # @staticmethod NOT USED
    # def add_keyword(t):
    #     RegexHandler.keywords.append(t.lower())

    @staticmethod
    def is_keyword(t):
        return bool(t.lower() in RegexHandler.keywords)

    # @staticmethod NOT USED
    # def get_keyword_id(t):
    #     return 0 if t.lower() not in RegexHandler.keywords else (RegexHandler.keywords.index(t.lower()) + 1)

    @staticmethod
    def get_emails(t, unique=True):
        """
        finds all email patterns in string
        @param t: string
        @param unique: bool
        @return: list of emails
        """
        emails = RegexHandler.email.findall(t)
        if unique:
            return list(sorted(set(emails)))
        return emails

    # @staticmethod NOT USED
    # def count_substr_in_str(substr, full_str):
    #     count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(substr), full_str))
    #     return count

    @staticmethod
    def get_domains_and_users(text, emails=None, return_emails=False):
        """
        Extract domain & user (first/last name) in a text (signature).
        we assume that the domain is in the email pattern and also in the urls
        and the user is in the email pattern
        @param text: string
        @param emails:
        @param return_emails:
        @return: list of domain, users and if needed also the emails
        """
        if emails is None:
            emails = []
        if not emails or type(emails) is not list:
            emails = RegexHandler.get_emails(str(text), unique=True)
        domains = []
        users = []
        for email in emails:
            domain = '.'.join(email.split('@')[1].split('.')[0:-1])
            domain = domain.split('.')[0]
            user = email.split('@')[0]
            domains.append(domain)
            users.append(user)
        if return_emails:
            return list(sorted(set((domains)))), list(sorted(set((users)))), list(sorted(set((emails))))
        return list(sorted(set((domains)))), list(sorted(set((users))))

    @staticmethod
    def get_domains(t, unique=True, no_social=False, emails=True, urls=True):
        """
        Extract the domain of the company from emails / urls in a string
        @param t: string (Text)
        @param unique: bool
        @param no_social: bool
        @param emails: list
        @param urls: list
        @return: list of domains
        """
        domains = []
        if emails:
            domains = ['.'.join(email.split('@')[1].split('.')[0:-1]) for email in RegexHandler.get_emails(t, unique)]
        if urls:
            urls = RegexHandler.get_urls(t, True)
            try:
                url_domains = [tldextract.extract(url).domain for url in urls]
                domains =  url_domains+domains
            except:
                for url in urls:
                    url_split = url.split('.')
                    if len(url_split) > 2:
                        if '.co.' in url:
                            domains += [url_split[-3]]
                        else:
                            domains += [url_split[-2]]
                    elif len(url_split) == 2:
                        if 'www' not in url_split[0].lower():
                            domains += [url_split[0]]
        if unique:
            domains = list(sorted(set(domains)))
        if no_social:
            social_domains = ['edgepilot', 'bit.ly', 'linkedin', 'goo', 'google', 'facebook', 'skype', 'pintrest',
                              'youtube', 'tinyurl', 'youtu.be']
            domains = list(filter(lambda domain: domain not in social_domains, domains))
        return domains

    @staticmethod
    def get_urls(t, unique=True):
        """
        Extracts the urls in a text (http://, www. etc.)
        @param t: Text
        @param unique: bool
        @return: list of urls
        """
        url = RegexHandler.url2.findall(t)
        urls = [x[0] for x in url]
        if unique:
            urls = list(sorted(set(urls)))
        return urls

    # @staticmethod NOT USED
    # def get_urls_old(t, unique=True):
    #     urls = RegexHandler.url.findall(t)
    #     if unique:
    #         z = []
    #         for ul in urls:
    #             ls = [ll for ll in list(sorted(set((ul))) if ll]
    #             z += ls
    #         return list(sorted(set((z)))
    #     return urls

    @staticmethod
    def get_emojis(t, unique=True):
        """
        Extract emojis in text
        @param t: text
        @param unique: bool
        @return: list of emojis
        """
        emojis = RegexHandler.emoji.findall(t)
        if unique:
            return list(sorted(set(emojis)))
        return emojis

    @staticmethod
    def remove_emojies(t):
        """
        removes emojis found in text
        @param t: text
        @return: text without emojis
        """
        return RegexHandler.emoji.sub(r'', t)

    @staticmethod
    def get_numbers(t, unique=True):
        """
        get all numbers in text
        @param t: text
        @param unique: bool
        @return: list of numbers in text
        """
        numbers = RegexHandler.number.findall(t)
        if unique:
            return list(sorted(set(numbers)))
        return numbers

    @staticmethod
    def contain_email(t):
        """
        checks if text contains an email pattern
        @param t: text
        @return: bool
        """
        return len(RegexHandler.get_emails(t)) > 0

    @staticmethod
    def contain_url(t):
        """
        checks if text contains a url pattern
        @param t: text
        @return: bool
        """
        return len(RegexHandler.get_urls(t)) > 0

    @staticmethod
    def contain_emoji(t):
        """
        checks if text contains an emoji
        @param t: text
        @return: bool
        """
        return len(RegexHandler.get_emojis(t)) > 0

    @staticmethod
    def contain_number(t):
        """
        checks if text contains a number
        @param t:
        @return: bool
        """
        return len(RegexHandler.get_numbers(t)) > 0

    @staticmethod
    def get_number_of_digits_in_number(n):
        """! This function return the number of digits in number
         @verbatim
         Args:
            n : Number
         Returns:
            digits: # of digits in the number.
         @endverbatim
         """
        if n == '':
            return 0
        if type(n) is str:
            return len(n)
        if n > 0:
            digits = int(math.log10(n)) + 1
        elif n == 0:
            digits = 1
        else:
            digits = int(math.log10(-n)) + 2  # +1 if you don't count the
        return digits

    @staticmethod
    def get_number_of_digits_and_digits_groups_in_text(t):
        """
        get all numbers and their number of digits in text
        @param t:
        @return: list of numbers and their digit amount
        """
        groups = []
        n_digits = 0
        group = ''
        for c in t:
            if c.isdigit():
                n_digits += 1
                group += c
            else:
                if len(group):
                    groups.append(group)
                    group = ''
        if len(group):
            groups.append(group)
        return n_digits, groups

    @staticmethod
    def get_users(text):
        """
        splitting the user from the email pattern and get all users from the emails
        @param text: string
        @return: list of users
        """
        emails = RegexHandler.get_emails(text, unique=True)
        users = []
        for email in emails:
            user = email.split('@')[0]
            users.append(user)
        return list(sorted(set((users))))

    # noinspection PyPep8Naming
    @staticmethod
    def now_as_string():
        """
        getting current date time as string in the format bellow
        @return: current datetime as string
        """
        currentDT = datetime.datetime.now()
        return currentDT.strftime("%a, %b %d, %Y at %I:%M:%S %p")

    @staticmethod
    def contain_month(t):
        """
        checks if text contains one of the calender months - january-december
        @param t: text
        @return: bool
        """
        for tt in RegexHandler.remove_punct(t.lower()).split():
            if tt in RegexHandler.months:
                return True
        return False

    @staticmethod
    def contain_day(t):
        """
        checks if text contains one of the weekly days - sunday-saturday
        @param t: text
        @return: bool
        """
        for tt in RegexHandler.remove_punct(t.lower()).split():
            if tt in RegexHandler.days:
                return True
        return False

    @staticmethod
    def is_time_format(t):
        """! Is time format is valid
          @verbatim
          Args:
             t : time
          Returns:
             bool : TRUE if time match the format
          @endverbatim
        """
        return bool(RegexHandler.time.match(t))

    @staticmethod 
    def has_time_format(t):
        """! Has time format.
          @verbatim
          Args:
             t : time
          Returns:
             bool : if input t, has the time format correctly - > return True.
          @endverbatim
        """
        t = t.lower().replace('am', ' ').replace('pm', ' ')
        r_list = RegexHandler.has_time.findall(t)
        if not len(r_list):
            return False
        else:
            for l in r_list:
                h = int(l[0])
                m = int(l[1])
                if h not in range(0, 25) or m not in range(0, 61):
                    return False
            return True

    @staticmethod
    def remove_html(t):
        """! Removing HTML template.
          @verbatim
          Args:
             t : text
          Returns:
             string : without html template
          @endverbatim
        """
        return RegexHandler.html.sub(r'', t)

    @staticmethod
    def merge_multiple_spaces(t):
        """
        turns multiple spaces to one
        @param t: text
        @return: text
        """
        return RegexHandler.merge_spaces.sub(r' ', t)

    @staticmethod
    def merge_multiple_new_lines(t):
        """! Merge multiple new lines.
          @verbatim
          Args:
             t : Text
          Returns:
             new text : merged lines (removed the \n ).
          @endverbatim
          """
        return RegexHandler.merge_lines.sub('\n', t).strip()

    @staticmethod
    def contain_camel_case(t):
        num_tokens_before_split_on_case = len(t.split())
        camel_case_splitted = RegexHandler.camelCase1.sub(r' \1', RegexHandler.camelCase2.sub(r' \1', t)).split()
        num_tokens_after_split_on_case = len(camel_case_splitted)
        return num_tokens_after_split_on_case > num_tokens_before_split_on_case

    @staticmethod
    def camel_to_snake(t):
        s1 = RegexHandler.camelCase3.sub(r'\1_\2', t)
        s2 = RegexHandler.camelCase4.sub(r'\1_\2', s1)
        if '_' in s2:
            # check if we have several UPPERS - if so split differently
            s3 = RegexHandler.camelCase5.sub(r'\1\2_', s2)
            return s3
        return s2

    @staticmethod
    def is_hashtag(t, edit=False):
        if t.startswith('#'):
            return True if not edit else (True, t.replace('#', ''))
        return False if not edit else (False, t)

    @staticmethod
    def is_user(t, edit=False):
        if t.startswith('@'):
            return True if not edit else (True, t.replace('@', ''))
        return False if not edit else (False, t)

    @staticmethod
    def contain_non_ascii_chars(t, edit=False, return_only_ascii=False):
        """
        counts the ascii, non ascii chars in the text.
        depend on the arguments, it can return:
            1. count of non ascii
            2. only the ascii chars
            3. count of non ascii chars, ascii chars, non ascii chars
        @param t:text
        @param edit: bool
        @param return_only_ascii: bool
        @return: decribed above
        """
        if not edit:
            return sum([(ord(s) >= 128) * 1 for s in t])
        asciis = ''
        non_asciis = ''
        for s in t:
            if ord(s) >= 128:
                non_asciis += s
            else:
                asciis += s
        if return_only_ascii:
            return asciis
        return len(non_asciis), asciis, non_asciis

    @staticmethod
    def remove_punct(text='', right=True, left=True, middle=True):
        """
        removes all punctuations from token (",",".","-", etc)
        by default it will remove all. in case given a specific direction, it
        start from it until reaches a non punctuations char
        @param text: text
        @param right: start from right side
        @param left: start from left side
        @param middle: do not modify most left and right chars
        @return: string
        """
        if right and left and middle:
            return text.translate(str.maketrans('', '', punctuation))

        token = text
        if left:
            while token and token[0] in punctuation:
                token = token[1:] if len(token) > 1 else ''

        if right:
            while token and token[-1] in punctuation:
                token = token[:-1] if len(token) > 1 else ''

        if middle and len(token) > 2:
            token = token[0] + token.translate(str.maketrans('', '', punctuation)) + token[-1]

        return token

    @staticmethod
    def remove_non_ascii_chars(t, right=True, left=True, middle=True):
        """

        removes all non ascii from token (",",".","-", etc)
        by default it will remove all. in case given a specific direction, it
        start from it until reaches a non ascii char
        @param text: text
        @param right: start from right side
        @param left: start from left side
        @param middle: do not modify most left and right chars
        @return: string
        """
        if right and left and middle:
            return ''.join([s for s in t if ord(s) < 128])
        else:
            if left:
                while t and ord(t[0]) >= 128:
                    t = t[1:] if len(t) > 1 else ''
            if right:
                while t and ord(t[-1]) >= 128:
                    t = t[:-1] if len(t) > 1 else ''
            if middle and len(t) > 2:
                t = t[0] + RegexHandler.remove_non_ascii_chars(t[1:-1]) + t[-1]
            return t

    @staticmethod
    def is_bad_decoding_line(line):
        """! Return if this line has bad decoding.
        @verbatim
        Args:
           line : Line
        Returns:
           bool : True if this line has bad decoding.
        @endverbatim
        """
        return len(re.findall(RegexHandler.bad_decoding, line, flags=0)) > 0

    @staticmethod
    def contain_date(tt):
        """! Check if the text contains date.
        @verbatim
        Args:
           tt : text we want to check if it's date.
        Returns:
           bool : True if contain date.
        @endverbatim
        """
        def remove_punct(s):
            return " ".join(s.translate(str.maketrans('', '', string.punctuation)).split()).strip()
    
        for t in tt.split():
            for marker in ['.', '|', '/', '-']:
                if marker in t:
                    if remove_punct(t).isdigit():
                        template = "%m/%d/%y" if '/' in t else "%m|%d|%y" if '|' in t else "%m-%d-%y" if '-' in t else "%m.%d.%y"
                        try:
                            datetime.datetime.strptime(t, template)
                            return True
                        except:
                            continue
                    continue
        return False

    @staticmethod
    def remove_brackets_content_from_email_text(text):
        # t = text.replace('[mailto:', '')
        #             t = RegexHandler.square_brackets.sub('', t)
        t = text.replace('[', '').replace(']', '')
        t = RegexHandler.brackets_cid.sub('', t)
        return t

    @staticmethod
    def extract_emojies_codes(input_string, check_first=True):
        """! Remove duplicates lines.
        @verbatim
        Args:
           input_string : String
           check_first(=True): Check input string if contains an emoji.
        Returns:
            returnString, emojies, ascies
        @endverbatim
        """
        if check_first:
            if not RegexHandler.contain_emoji(input_string):
                return input_string
    
        returnString = ""
        emojies = []
        ascies = []
        for character in input_string:
            try:
                character.encode("ascii")
                returnString += character
            except UnicodeEncodeError:
                replaced = unidecode(str(character))
                if replaced != '':
                    returnString += replaced
                    ascies += [character]
                else:
                    try:
                        emojies += [unicodedata.name(character).replace(' ', '_')]
                    except ValueError:
                        ascies += [character]
    
        return returnString, emojies, ascies

    @staticmethod
    def normalize_space(text):
        """
        Remove multiple space characters and keep single simple space. Also stripping new lines ending the text input.
        :param text: string input
        :return: processed string
        """
        return '\n'.join([' '.join(line.split()) for line in text.strip().split('\n')])

    # noinspection RegExpSingleCharAlternation
    @staticmethod
    def remove_space_before_semicolon(text):
        """
        Replace any non alphanumeric character preceded and followed by a space, with the character without space
        preceding. For example: 'Mobile : 972-54654' will output: 'Mobile: 972-54654'
        :param text: string input
        :return: processed string
        """
        # return re.sub(r'\s+(:|,)', r'\1 ', text)
        return RegexHandler.semicolon_spaces.sub(r'\1 ', text)

    @staticmethod
    def remove_brackets_for_digits(text):
        """
        Remove brackets around one or more digits that may be preceded by a plus sign (+). The output is the digits
        with the plus sign if present without the beackets.
        :param text: string input
        :return: processed string
        """
        # return re.sub(r'\(\s?(\+?\d+)\s?\)', r'\1', text)
        return RegexHandler.digits_brackets.sub(r'\1',text)

    @staticmethod
    def count_sequential_digits(text, get_all=False):
        """
        fetches all numbers in text, and depends on the get_all argument it returns either the
        max length number, or the length of all numbers
        @param text: text
        @param get_all: bool
        @return: list of lengths
        """
        # matches = re.findall(r'\d[\d\s\-.]+\d', text)
        matches = re.findall(r'\d+', RegexHandler.remove_punct(text))
        if matches:
            if not get_all:
                return max([len([m for m in match if m.isdigit()]) for match in matches])
            else:
                return [len([m for m in match if m.isdigit()]) for match in matches]
        return 0 if not get_all else [0]

    # noinspection RegExpSingleCharAlternation
    @staticmethod
    def insert_space(text):
        """
        replace chars that represents a separation with whitespace
        @param text: text
        @return: text
        """
        # return re.sub(r'(\*|~|\|)', r' \1 ', text)
        return RegexHandler.rep_with_space.sub(r' \1 ', text)

    @staticmethod
    def split_x_number(text):
        """
        in case of extentions that appear as "x", we split the number and the "x"
        @param text:  text
        @return: text
        """
        # return re.sub(r'\bx(\d+)\b', r'x \1', text)
        return RegexHandler.number_with_x.sub(r'x \1',text)

    @staticmethod
    def split_number_non_number(text):
        """
        if we have this pattern phone-123456, we want to split the "phone" from the nymber itself
        we have a special treatment for linkedin profiles that do have such pattern and we keep them as is
        @param text: text
        @return:text
        """
        # don't separate linkedin profile numbers
        text = re.sub(r'(linkedin\.com/in/)([\w]+-[\w]+)-(\d{6,20})', r'\1\2_\3', text)
        text = re.sub(r'\b([a-zA-Z]+)-(\d{6,20})\b', r'\1 \2', text)
        text = re.sub(r'(linkedin\.com/in/)([\w]+-[\w]+)_(\d{6,20})', r'\1\2-\3', text)
        return text  # re.sub(r'\b([a-zA-Z]+)-(\d{6,20})\b', r'\1 \2', text)

    # noinspection RegExpRedundantEscape
    @staticmethod
    def concat_numbers(text):
        """
        when there are two phone/mobile numbers separated with white space, we will add ","
        between them for easier preprocessing
        @param text: text
        @return: text
        """
        # text = re.sub(r'(\d{6,20}/\d*)\s+(\d{8,20})', r'\1, \2', text)
        # text = re.sub(r'(\d{5,20})\s+(\d{3}-\d+\D*)', r'\1, \2', text)
        # text = re.sub(r'(\d{3,4}-\d{3,4})\s+(\d+-\d+)', r'\1, \2', text)
        # text = re.sub(r'(\d{6,20})\s+(\d{5,20})', r'\1, \2', text)
        text = RegexHandler.concat_phones1.sub(r'\1, \2', text)
        text = RegexHandler.concat_phones2.sub(r'\1, \2', text)
        text = RegexHandler.concat_phones3.sub(r'\1, \2', text)
        text = RegexHandler.concat_phones4.sub(r'\1, \2', text)

        # text = re.sub(r'(?<=\d) (?=\d)', '-', text)
        text = re.sub(r'(?<=[^a-zA-Z][\d+\-\(\)]) (?=[\d\-\(\)][^a-zA-Z])', '-', text)  # dorons fix
        # text = '\n'.join([re.sub(r'(?<=\d)+\s+(?=\d+(\s|\b))', '-', line) for line in text.split('\n')])
        # text = re.sub(r'([\s-]\d+)( )(\d+\s)', r'\1-\3', text)
        # text = re.sub(r'([\s-]\d+)( )(\d+\s)', r'\1-\3', text)
        # text = re.sub(r'(^\d+)( )(\d+[\s-])', r'\1-\3', text)
        # text = re.sub(r'([\s-]\d+)( )(\d+$)', r'\1-\3', text)

        return text

    @staticmethod
    def fix_url(text):
        """
        adds www to token that contains a know domain for later use in connections handler
        @param text: text
        @return: text
        """
        line_l = text.split('\n')
        line_l_out = []
        for line in line_l:
            token_l = line.split(' ')
            token_l_out = []
            for token in token_l:
                if '@' not in token and re.findall(r'\S+(\.org|\.gov|\.com|\.net|\.int|\.edu|\.mil)(\s|$)', token):
                    if not token.startswith('www.'):
                        token_l_out.append('www.' + token)
                    else:
                        token_l_out.append(token)
                else:
                    token_l_out.append(token)
            line_l_out.append(' '.join(token_l_out))
        return '\n'.join(line_l_out)

    @staticmethod
    def clear_url_junk(text):
        """
        detect patterns of url junk such %3A%2F%2F and removes it
        @param text: text
        @return: text
        """
        token_l = text.split()
        token_l_out = []
        for token in token_l:
            if token.count('%') > 1:
                if len(RegexHandler.url_junk.findall(token)) == len(token):
                    continue
                else:
                    token_l_out.append(token)
            else:
                token_l_out.append(token)
        return ' '.join(token_l_out)

    @staticmethod
    def clear_contact_prefixes(text):
        """
        removes the contact prefix (emial:, linkedin:, twittwer, etc)
        @param text: text
        @return: text
        """
        # return re.sub(RegexHandler.contact_prefixes_pattern, '', text, flags=re.IGNORECASE)
        return RegexHandler.contact_prefixes.sub('', text)

    # noinspection RegExpRedundantEscape
    @staticmethod
    def clear_number_suffixes(text):
        """
        TODO daniela add description of this regex
        @param text:
        @return:
        """
        return re.sub(r'([\d\-\(\)\.\+]{5})_([a-zA-Z]+)($|\s)', r'\1 \2\3', text)

    @staticmethod
    def get_digits(text):
        """
        Extract only digits from number
        @param text: string to process
        @return: ordered digits in string
        """
        return ''.join(re.findall(r'\d', text))

    # @staticmethod
    # def split_line_by_separator(text):
    #     split_sep = RegexHandler.split_by_separator(text)
    #     if len(split_sep) == 2:
    #         if len(split_sep) >= 2:
    #             return '\n'.join(split_sep)
    #     return text
    #
    # # noinspection RegExpRedundantEscape
    # @staticmethod
    # def split_by_separator(text):
    #     return RegexHandler.split_by_separator.split(text)
