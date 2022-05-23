import datetime
from . import GlossTxt


class GlossEntry(GlossTxt.GlossTxt):
    '''Object for an individual glossary entry'''
    def __init__(self, name, acronym_full="", definition="", furtherreading="", institute="",
            pronunciation="", seealso="", updated=datetime.date.today()):
        '''
        name - entry's name; spaces are supported, do not use [brackets]
        acronym_full - if acronym, what is the full name. if blank, assumed to not be an acronym.
        further_reading - URL to a webpage, usually an "official" one associated with the term
        institute - which institution is the phrase associated with?
        pronunciation - pronunciation (ex: wdl - "widdle")
        seealso - related but not equivalent entries, such as CLI being related to Dockstore CLI.
        updated - when the entry was last updated

        When outputting to RST, acronym_full and definition will replace text in [brackets]
        with a working internal hyperlink to another entry. For example, if self.definition="I use
        [Seven Bridges]", then the RST out will be "I use :ref:`dict Seven Bridges`" (although the
        link will not be clickable if there is no entry for Seven Bridges)
        '''
        self.name: str = name
        self.acronym_full: str = acronym_full
        self.definition: str = definition
        self.furtherreading: str = furtherreading
        self.institute: bool = institute
        self.pronunciation: str = pronunciation
        self.seealso: str = seealso
        self.updated: datetime = updated

    def return_name(self, nospaces:bool = False):
        '''Returns name of the entry'''
        if not nospaces:
            return self.name
        else:
            processed_characters = []
            for character in self.return_name(nospaces=False):
                if character == " ":
                    character = "-"
                processed_characters.append(character)
            return "".join(processed_characters)

    def text_entry_title(self):
        '''Return underlined title. Same in RST, Markdown, and plaintext.'''
        entry_title = []
        entry_title.append("\n\n")  # keep space between entries big enough to keep RST happy
        entry_title.extend(self.underline_text(self.name))
        return "".join(entry_title)

    def text_pronunciation(self, format:str = "txt"):
        '''Return pronunciation'''
        if format == "txt":
            return f"[pronounced {self.pronunciation}]\n"
        elif format == "rst":
            return f"[pronounced {self.pronunciation}]  \n\n"

    def text_acronym(self, format:str = "txt"):
        '''Return acronym's full form, in italics if RST. We need an extra newline in RST to prevent
        the acronym from being considered a header relative to the definition.'''
        if format == "txt":
            return f"abbreviation for {self.acronym_full}\n"
        elif format == "rst":
            words = self.acronym_full.split()
            return f"*abbreviation for* {self.rst_process_brackets(words)}  \n\n"

    def text_definition(self, format:str = "txt"):
        '''Return the definition of the entry.
        If RST, calls a function that turns bracketed [text] into internal links.
        Limitations: RST does not support letters coming after a link without a puncuation mark.'''
        if format == "txt":
            return f"    {self.definition}\n"
        elif format == "rst":
            words = self.definition.split()
            processed_with_links = self.rst_process_brackets(words)
            return f"    {processed_with_links}  \n\n"

    def text_institute(self, format:str = "txt"):
        '''Return a caveat about how this term may mean something else outside the context of
        self.institute. In RST form this becomes a note block.'''
        if format == "txt":
            return f"This term as we define it here is associated with {self.institute} and may have different definitions in other contexts.\n"
        elif format == "rst":
            return f".. note:: This term as we define it here is associated with {self.institute} and may have different definitions in other contexts.  \n"

    def text_seealso(self, format:str = "txt"):
        '''Returns the entry's seealso information, which links to another entry.
        There is a supposedly simplier way to do this with sphinx.ext.autosectionlabel, via:
            see also :ref:`{self.seealso}`
        ...but using extension often requires people reformat tons of links. For example, in
        Dockstore's documentation, loading sphinx.ext.autosectionlabel raises 175 new errors.'''
        if format == "txt":
            return f"see also {self.seealso}\n"
        elif format == "rst":
            words = self.seealso.split()
            processed_with_links = self.rst_process_brackets(words)

            # if there is an institute, it's a good idea to include an extra newline. it's
            # not strictly necessary to render properly, but without it, a warning will be thrown
            if self.institute == "":
                return f"see also {processed_with_links}  \n"
            else:
                return f"\nsee also {processed_with_links}  \n"

    def text_furtherreading(self, format:str = "txt"):
        '''Returns the entry's further reading section, which is a single URL.
        In RST, if there is a see also, we need an extra newline in further reading.'''
        if format == "txt":
            return f"Further reading: {self.furtherreading}\n"
        elif format == "rst":
            furtherreading = []

            # start with extra newline if necessary
            if self.seealso == "" and self.institute == "":
                pass
            else:
                furtherreading.append("\n")

            furtherreading.append("Further reading: ")

            # check if link is internal or external
            if (self.furtherreading.startswith("https://")
                    or self.furtherreading.startswith("http://")
                    or self.furtherreading.startswith("www")):
                # assume external link
                furtherreading.append(f"{self.rst_url(self.furtherreading)}  \n")
            else:
                # assume internal documentation link
                furtherreading.append(f"{self.rst_url(self.furtherreading, internal=True)}  \n")

            return "".join(furtherreading)

    def text_updated(self, format:str = "txt"):
        '''Return when entry was last updated (visibly if txt, as a comment if RST)
        Caveat: This isn't very helpful if you keep all of your entries in the same file and
        parse all of them at the same time.'''
        if format == "txt":
            return self.updated.strftime("updated %Y-%m-%d\n")
        elif format == "rst":
            return self.updated.strftime("\n.. updated %Y-%m-%d  \n\n\n\n")

    def generate_plaintext(self, timestamp:bool = False):
        '''Generate plaintext output of this entry'''
        plaintext = []
        plaintext.append(self.text_entry_title())
        if self.pronunciation != "":
            plaintext.append(self.text_pronunciation())
        if self.acronym_full != "":
            plaintext.append(self.text_acronym())
        if self.definition != "":
            plaintext.append(self.text_definition())
        if self.institute != "":
            plaintext.append(self.text_institute())
        if self.seealso != "":
            plaintext.append(self.text_seealso())
        if self.furtherreading != "":
            plaintext.append(self.text_furtherreading())
        if timestamp:
            plaintext.append(self.text_updated())
        else:
            plaintext.append("\n\n\n")
        return "".join(plaintext)

    def generate_RST(self, timestamp:bool = False):
        '''Generate RST output of this entry'''
        rst = []
        rst.append(self.rst_bookmark())
        rst.append(self.text_entry_title())
        if self.pronunciation != "":
            rst.append(self.text_pronunciation(format="rst"))
        if self.acronym_full != "":
            rst.append(self.text_acronym(format="rst"))
        if self.definition != "":
            rst.append(self.text_definition(format="rst"))
        if self.institute != "":
            rst.append(self.text_institute(format="rst"))
        if self.seealso != "":
            rst.append(self.text_seealso(format="rst"))
        if self.furtherreading != "":
            rst.append(self.text_furtherreading(format="rst"))
        if timestamp:
            rst.append(self.text_updated(format="rst"))
        else:
            # minimum of one newline needed to keep rst bookmarks working
            rst.append("\n\n\n")
        return "".join(rst)
