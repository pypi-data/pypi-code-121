from clld.web.datatables.base import DataTable
from clld.web.datatables.base import LinkCol
from clld.web.datatables.sentence import Sentences, AudioCol

class Texts(DataTable):
    def col_defs(self):
        return [LinkCol(self, "name")]



class SentencesWithAudio(Sentences):

    def col_defs(self):
        return super().col_defs() + [AudioCol(self, "audio")]
