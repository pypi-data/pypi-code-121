from .reference import ReferenceFileModel

__all__ = ['MirMrsXArtCorrModel']


class MirMrsXArtCorrModel(ReferenceFileModel):
    """
    A data model for MIRI MRS cross-artifact corrections file.

    Parameters
    __________
    init : any
        Any of the initializers supported by `~jwst.datamodels.DataModel`.

    ch1a_table : numpy table
         Cross artifact correction parameters for Channel 1A

    ch1b_table : numpy table
         Cross artifact correction parameters for Channel 1B

    ch1c_table : numpy table
         Cross artifact correction parameters for Channel 1C

    """
    schema_url = "http://stsci.edu/schemas/jwst_datamodel/miri_mrsxartcorr.schema"
