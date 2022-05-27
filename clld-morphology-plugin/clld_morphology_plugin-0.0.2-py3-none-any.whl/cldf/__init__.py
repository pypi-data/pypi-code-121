from clldutils import jsonlib
try:
    from importlib.resources import files  # pragma: no cover
except ImportError:  # pragma: no cover
    from importlib_resources import files  # pragma: no cover


cldf_path = files("clld_morphology_plugin") / "cldf"
FormSlices = jsonlib.load(cldf_path / f"FormSlices-metadata.json")
MorphsetTable = jsonlib.load(cldf_path / f"MorphsetTable-metadata.json")
MorphTable = jsonlib.load(cldf_path / f"MorphTable-metadata.json")
