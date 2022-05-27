import re
from clld.db.meta import DBSession
from clld.db.models import common as models
from clld.web.util.helpers import link
from clld.web.util.htmllib import HTML
from markupsafe import Markup
from sqlalchemy import or_


try:
    from clld_morphology_plugin.util import rendered_gloss_units
except ImportError:

    def rendered_gloss_units(request, sentence):
        units = []
        if sentence.analyzed and sentence.gloss:
            slices = {sl.index: sl for sl in sentence.forms}
            g_shift = 0 # to keep up to date with how many g-words there are in total
            for pwc, (pword, pgloss) in enumerate(
                zip(sentence.analyzed.split("\t"), sentence.gloss.split("\t"))
            ):
                g_words = []
                glosses = []
                for gwc, (word, gloss) in enumerate(
                    zip(pword.split("="), pgloss.split("="))
                ):  
                    i = pwc + gwc + g_shift
                    if gwc > 0:
                        g_shift += 1
                        for glosslist in [g_words, glosses]:
                            glosslist.append("=")
                    if i not in slices:
                        g_words.append(HTML.span(word))
                        glosses.append(HTML.span(gloss))
                    else:
                        g_words.append(HTML.span(link(request, slices[i].form), name=slices[i].form.id))
                        glosses.append(HTML.span(gloss))
            
                units.append(
                    HTML.div(
                        HTML.div(*g_words),
                        HTML.div(*glosses, **{"class": "gloss"}),
                        class_="gloss-unit",
                    )
                )

        return units


GLOSS_ABBR_PATTERN = re.compile(
    "(?P<personprefix>1|2|3)?(?P<abbr>[A-Z]+)(?P<personsuffix>1|2|3)?(?=([^a-z]|$))"
)


def gloss_with_tooltip(gloss, abbrs):
    person_map = {"1": "first person", "2": "second person", "3": "third person"}

    res = []
    end = 0
    for match in GLOSS_ABBR_PATTERN.finditer(gloss):
        if match.start() > end:
            res.append(gloss[end : match.start()])

        abbr = match.group("abbr")
        if abbr in abbrs:
            explanation = abbrs[abbr]
            if match.group("personprefix"):
                explanation = f"{person_map[match.group('personprefix')]} {explanation}"

            if match.group("personsuffix"):
                explanation = f"{explanation} {person_map[match.group('personsuffix')]}"

            res.append(
                HTML.span(
                    HTML.span(gloss[match.start() : match.end()].lower(), class_="sc"),
                    **{"data-hint": explanation, "class": "hint--bottom"},
                )
            )
        else:
            res.append(
                (match.group("personprefix") or "")
                + abbr  # noqa: W504
                + (match.group("personsuffix") or "")  # noqa: W504
            )

        end = match.end()

    res.append(gloss[end:])
    return filter(None, res)


def rendered_sentence(
    request,
    sentence,
    abbrs=None,
    in_context=True,
    text_link=True,
    sentence_link=False,
    counter_class="example",
):
    """Format a sentence as HTML."""
    if sentence.xhtml:
        return HTML.div(
            HTML.div(Markup(sentence.xhtml), class_="body"), class_="sentence"
        )

    if abbrs is None:
        q = DBSession.query(models.GlossAbbreviation).filter(
            or_(
                models.GlossAbbreviation.language_pk == sentence.language_pk,
                models.GlossAbbreviation.language_pk is None,
            )
        )
        abbrs = dict((g.id, g.name) for g in q)

    units = rendered_gloss_units(request, sentence)

    if sentence_link:
        surface = HTML.div(
            link(request, sentence, label=sentence.name), class_="object-language"
        )
    else:
        surface = HTML.div(sentence.name, " ", class_="object-language")
    if text_link:
        text = sentence.text_assocs[0].text
        text_ref = (
            " ("
            + link(request, text, label=text.id, url_kw={"_anchor": sentence.id})
            + ")"
        )
    else:
        text_ref = ""

    if sentence.audio:
        audio_content = HTML.audio(
            "",
            HTML.source(src=f"/audio/{sentence.audio}", type="audio/x-wav"),
            controls="controls",
            preload="none"
        )
    else:
        audio_content = ""

    sentence_content = HTML.div(
        HTML.div(
            HTML.a(id=sentence.id),
            HTML.div(
                HTML.div(sentence.original_script, class_="original-script")
                if sentence.original_script
                else "",
                surface,
                HTML.div(*units, **{"class": "gloss-box"}) if units else "",
                HTML.div(
                    HTML.span(sentence.description, class_="translation"), text_ref
                )
                if sentence.description
                else "",
                class_="body",
            ),
            class_="sentence",
        ),
        audio_content,
        class_="sentence-wrapper",
    )
    if in_context:
        return HTML.li(sentence_content, class_=counter_class, id_=sentence.id)
    return sentence_content
