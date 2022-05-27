from clld.db.models.common import Language
from clld.web.datatables.base import Col
from clld.web.datatables.base import DataTable
from clld.web.datatables.base import LinkCol
from sqlalchemy.orm import joinedload
from clld_morphology_plugin import models
from clld.web.util.helpers import icon
from sqlalchemy import and_

class DescriptionLinkCol(LinkCol):

    """Render a link to the unit using the description as label."""

    def get_attrs(self, item):
        return {"label": item.description}


class AudioCol(Col):
    def __init__(self, dt, name, **kw):
        kw['choices'] = ['yes']
        kw['input-size'] = 'mini'
        kw['model_col'] = models.Wordform_files.id
        Col.__init__(self, dt, name, **kw)

    def format(self, item):
        if item.audio:
            return icon('volume-up')

    def order(self):
        return models.Wordform_files.id

    def search(self, qs):
        if qs == 'yes':
            return models.Wordform_files.pk != 0

class Wordforms(DataTable):

    __constraints__ = [Language]

    def base_query(self, query):
        query = query.join(Language).options(joinedload(models.Wordform.language))


        query = query\
            .outerjoin(
                models.Wordform_files,
                and_(
                    models.Wordform_files.object_pk == models.Wordform.pk,
                    models.Wordform_files.mime_type.contains('audio/')))\
            .options(joinedload(models.Wordform._files))

        if self.language:
            return query.filter(models.Wordform.language == self.language)
        return query

    def col_defs(self):
        return [
            LinkCol(self, "name"),
            Col(self, "description"),
            LinkCol(
                self, "language", model_col=Language.name, get_obj=lambda i: i.language
            ),
            AudioCol(self, "Audio")
        ]

class Morphs(DataTable):

    __constraints__ = [Language]

    def base_query(self, query):
        query = query.join(Language).options(joinedload(models.Morph.language))

        if self.language:
            return query.filter(models.Morph.language == self.language)
        return query

    def col_defs(self):
        return [
            LinkCol(self, "name"),
            Col(self, "description"),
            LinkCol(
                self, "language", model_col=Language.name, get_obj=lambda i: i.language
            ),
        ]


class Morphemes(DataTable):
    __constraints__ = [Language]

    def base_query(self, query):
        query = query.join(Language).options(joinedload(models.Morpheme.language))

        if self.language:
            return query.filter(models.Morpheme.language == self.language)
        return query

    def col_defs(self):
        return [
            LinkCol(self, "name"),
            Col(self, "description"),
            LinkCol(
                self, "language", model_col=Language.name, get_obj=lambda i: i.language
            ),
        ]


class Meanings(DataTable):
    def col_defs(self):
        return [LinkCol(self, "name")]
