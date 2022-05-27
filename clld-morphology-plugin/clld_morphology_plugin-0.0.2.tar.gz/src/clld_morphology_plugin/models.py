from clld.db.meta import Base
from clld.db.meta import PolymorphicBaseMixin
from clld.db.models.common import Contribution
from clld.db.models.common import HasSourceMixin, FilesMixin, HasFilesMixin
from clld.db.models.common import IdNameDescriptionMixin
from clld.db.models.common import Language
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from zope.interface import implementer
from clld_morphology_plugin.interfaces import IMeaning
from clld_morphology_plugin.interfaces import IMorph
from clld_morphology_plugin.interfaces import IMorphset
from clld_morphology_plugin.interfaces import IWordform


@implementer(IMeaning)
class Meaning(Base, PolymorphicBaseMixin, IdNameDescriptionMixin):
    pass


@implementer(IMorphset)
class Morpheme(Base, PolymorphicBaseMixin, IdNameDescriptionMixin, HasSourceMixin):
    __table_args__ = (UniqueConstraint("language_pk", "id"),)

    language_pk = Column(Integer, ForeignKey("language.pk"), nullable=False)
    language = relationship(Language, innerjoin=True)

    contribution_pk = Column(Integer, ForeignKey("contribution.pk"))
    contribution = relationship(Contribution, backref="morphemes")


@implementer(IMorph)
class Morph(Base, PolymorphicBaseMixin, IdNameDescriptionMixin, HasSourceMixin):
    __table_args__ = (
        UniqueConstraint("language_pk", "id"),
        UniqueConstraint("morpheme_pk", "id"),
    )

    language_pk = Column(Integer, ForeignKey("language.pk"), nullable=False)
    language = relationship(Language, innerjoin=True)
    morpheme_pk = Column(Integer, ForeignKey("morpheme.pk"), nullable=False)
    morpheme = relationship(Morpheme, innerjoin=True, backref="allomorphs")


class MorphemeMeaning(Base):
    id = Column(String, unique=True)
    morpheme_pk = Column(Integer, ForeignKey("morpheme.pk"), nullable=False)
    meaning_pk = Column(Integer, ForeignKey("meaning.pk"), nullable=False)
    morpheme = relationship(Morpheme, innerjoin=True, backref="meanings")
    meaning = relationship(Meaning, innerjoin=True, backref="morphemes")

@implementer(IWordform)
class Wordform(Base, PolymorphicBaseMixin, IdNameDescriptionMixin, HasSourceMixin, HasFilesMixin):
    __table_args__ = (UniqueConstraint("language_pk", "id"),)

    language_pk = Column(Integer, ForeignKey("language.pk"), nullable=False)
    language = relationship(Language, innerjoin=True)

    contribution_pk = Column(Integer, ForeignKey("contribution.pk"))
    contribution = relationship(Contribution, backref="wordforms")

    segmented = Column(String)

    @property
    def audio(self):
        for f in self._files:
            if f.mime_type.split('/')[0] == 'audio':
                return f
                
class FormMeaning(Base):
    id = Column(String, unique=True)
    form_pk = Column(Integer, ForeignKey("wordform.pk"), nullable=False)
    meaning_pk = Column(Integer, ForeignKey("meaning.pk"), nullable=False)
    form = relationship(Wordform, innerjoin=True, backref="meanings")
    meaning = relationship(Meaning, innerjoin=True, backref="forms")

class FormSlice(Base):
    form_pk = Column(Integer, ForeignKey("wordform.pk"))
    morph_pk = Column(Integer, ForeignKey("morph.pk"))
    morpheme_meaning_pk = Column(Integer, ForeignKey("morphememeaning.pk"))
    form_meaning_pk = Column(Integer, ForeignKey("formmeaning.pk"))
    form = relationship(Wordform, backref="morphs")
    morph = relationship(Morph, backref="forms")
    index = Column(Integer)
    form_meaning = relationship(FormMeaning)
    morpheme_meaning = relationship(MorphemeMeaning, backref="morph_tokens")

class Wordform_files(Base, FilesMixin):
    pass