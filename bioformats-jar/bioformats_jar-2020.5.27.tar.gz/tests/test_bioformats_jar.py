from pathlib import Path

from bioformats_jar import get_loci, get_ome, set_loci_log_level


def test_import():
    loc = get_loci()

    from bioformats_jar import loci

    assert loc is loci

    assert loci.formats
    assert loci.common
    assert loci.poi

    set_loci_log_level("INFO")


def test_read():
    loci = get_loci()
    reader = loci.formats.ImageReader()
    factory = loci.common.services.ServiceFactory()
    service = factory.getInstance(loci.formats.services.OMEXMLService)
    reader.setMetadataStore(service.createOMEXMLMetadata())
    reader.setId(str(Path(__file__).parent / "sample.czi"))
    assert str(reader.getMetadataStore().dumpXML())
    assert reader.openBytes(0)[0] != 0


def test_get_ome():
    o = get_ome()
    from bioformats_jar import ome

    assert o is ome
