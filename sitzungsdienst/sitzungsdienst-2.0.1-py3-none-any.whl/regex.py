import re


ASSIGNMENT = re.compile(r"""
    (?P<where>(?:.*?)?)\s?                      # (1) .. location (optional)
    (?P<time>\d{2}:\s?\d{2})\s                  # (2) .. time of court date
    (?P<docket>\d{2,3}\sU?Js\s\d+\/\d{2})\s     # (3) .. docket number
    (?P<assigned>
        (?:                                     # (4) .. name(s) of prosecutor(s), namely ..
            (?:(?:Dr\.\s)?[\u00C0-\u017F\w-]+)  # (a) .. last name & doctoral degree (optional)
            (?:\s?(?:\([0-9XIV]+\)))?\s?,\s     # (b) .. department number (optional)
            (?:[\u00C0-\u017F\w-]+)\s?,\s       # (c) .. first name
            (?:                                 # (d) .. official title
                (?:
                    Ref|JOI|AAAnw|
                    E?(?:O?StA|O?AA)|
                    (?:RR(?:\'in)?aAA)
                )
                (?:\'in)?
                (?:\s\(ba\))?
            )\s?
        )+
    )
""", re.VERBOSE)


EXPRESS = re.compile(r"""
    (?P<from>\d{2}\.\d{2}\.\d{4})\s             # (1) .. start date
    (?:-\s)                                     # (2) .. hyphen, followed by whitespace
    (?P<to>\d{2}\.\d{2}\.\d{4})\s               # (3) .. end date
    (?P<assigned>
        (?:                                     # (4) .. name(s) of prosecutor(s), namely ..
            (?:(?:Dr\.\s)?[\u00C0-\u017F\w-]+)  # (a) .. last name & doctoral degree (optional)
            (?:\s(?:\([0-9XIV]+\)))?\s?,\s      # (b) .. department number (optional)
            (?:[\u00C0-\u017F\w-]+)\s?,\s       # (c) .. first name
            (?:                                 # (d) .. official title
                (?:
                    Ref|JOI|AAAnw|
                    E?(?:O?StA|O?AA)|
                    (?:RR(?:\'in)?aAA)
                )
                (?:\'in)?
                (?:\s\(ba\))?
            )\s?
        )+
    )
""", re.VERBOSE)


PERSON = re.compile(r"""
    (?P<doc>(?:Dr\.)?)\s??                     # (1) .. doctoral degree (optional)
    (?P<last>[\u00C0-\u017F\w-]+)\s?           # (2) .. last name
    (?P<department>(?:\([0-9XIV]+\))?)\s?,\s?  # (3) .. department number (optional)
    (?P<first>[\u00C0-\u017F\w-]+)\s?,\s?      # (4) .. first name
    (?P<title>                                 # (5) .. official title, being either ..
        (?:
            # (a) .. Rechtsreferendar:in
            # - Ref / Ref'in
            #
            # (b) .. Justizoberinspektor:in
            # - JOI / JOI'in
            #
            # (c) .. Amtsanwaltsanwärter:in
            # - AAAnw / AAAnw'in
            Ref|JOI|AAAnw|

            # (d) .. (Erste:r / Ober-) Staatsanwalt:anwältin
            # - OStA / OStA'in
            # - EStA / EStA'in
            # - StA / StA'in
            # (e) .. (Erste:r) (Oberamts-) Anwalt:Anwältin
            # - EOAA / EOAA'in
            # - OAA / OAA'in
            E?(?:O?StA|O?AA)|

            # (f) .. Regierungsrat:rätin als Amtsanwalt:anwältin
            # - RRaAA / RR'inaAA'in
            (?:RR(?:\'in)?aAA)
        )
        (?:\'in)?
        (?:\s\(ba\))?
    )
""", re.VERBOSE)
