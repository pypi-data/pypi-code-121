from clld_morphology_plugin import interfaces
from clld_morphology_plugin import models
from clld_morphology_plugin import datatables


__author__ = "Florian Matter"
__email__ = "florianmatter@gmail.com"
__version__ = "0.0.2"


def includeme(config):
    config.registry.settings["mako.directories"].insert(
        1, "clld_morphology_plugin:templates"
    )
    config.add_static_view(
        "clld-morphology-plugin-static", "clld_morphology_plugin:static"
    )

    config.register_resource("morph", models.Morph, interfaces.IMorph, with_index=True)
    config.register_resource(
        "morpheme",
        models.Morpheme,
        interfaces.IMorphset,
        with_index=True,
        with_detail=True,
    )
    config.register_resource(
        "meaning", models.Meaning, interfaces.IMeaning, with_index=True
    )
    config.register_resource(
        "wordform", models.Wordform, interfaces.IWordform, with_index=True
    )

    config.register_datatable("meanings", datatables.Meanings)
    config.register_datatable("morphs", datatables.Morphs)
    config.register_datatable("wordforms", datatables.Wordforms)
    config.register_datatable("morphemes", datatables.Morphemes)
