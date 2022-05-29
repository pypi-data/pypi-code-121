import strax
import straxen
import wfsim
import pema
import os

export, __all__ = strax.exporter()


@export
def pema_context(
        base_dir: str,
        fax_config: str,
        cmt_run_id_sim: str,
        config_update: dict = None,
        cmt_version='global_v8',
        raw_dir=None,
        data_dir=None,
        raw_types=None,
) -> strax.Context:
    """
    Central context for pema, allows to init from a config.
    :param base_dir: Where store instructions,
    :param fax_config: fax configuration file
    :param cmt_run_id_sim: run_id for CMT (see straxen.contexts.xenonnt_simulation)
    :param config_update: Setup the config of the context
    :param raw_dir: Where to store the low level datatypes
    :param data_dir: Where to store the high level datatypes
    :param raw_types: Low level datatypes, stored separately from
        high level datatypes
    :return: context
    """
    if not os.path.exists(base_dir):
        raise FileNotFoundError(
            f'Cannot use {base_dir} as base_dir. It does not exist.')

    config = dict(detector='XENONnT',
                  check_raw_record_overlaps=False,
                  fax_config=fax_config,
                  cmt_run_id_sim=cmt_run_id_sim,
                  )

    if config_update is not None:
        if not isinstance(config_update, dict):
            raise ValueError(f'Invalid config update {config_update}')
        config = strax.combine_configs(config, config_update)
    context_options = dict(
        free_options= ('n_nveto_pmts', 'channel_map', 'n_mveto_pmts',
                       'gain_model_nv', 'gain_model_mv', 'cmt_run_id_sim'),
    )
    st = straxen.contexts.xenonnt_simulation(
        fax_config=config['fax_config'],
        cmt_run_id_sim=cmt_run_id_sim,
        cmt_version=cmt_version,
        **context_options
    )
    st.set_config(config)

    # Setup the plugins for nT
    # st.register(wfsim.RawRecordsFromFaxNT)
    st.register_all(pema.match_plugins)
    st.register_all(straxen.plugins.position_reconstruction)
    del st._plugin_class_registry['peak_positions_base_nt']
    st._plugin_class_registry['peaks'].save_when = strax.SaveWhen.ALWAYS

    if raw_types is None:
        raw_types = (wfsim.RawRecordsFromFaxNT.provides +
                     straxen.plugins.pulse_processing.PulseProcessing.provides)

    # Setup the storage, don't trust any of the stuff we get from xenonnt_simulation
    st.storage = []

    if raw_dir is not None:
        st.storage += [strax.DataDirectory(
            raw_dir,
            take_only=raw_types)]
    if data_dir is not None:
        st.storage += [strax.DataDirectory(
            data_dir,
            exclude=raw_types
        )]
    if not st.storage or not len(st.storage):
        raise RuntimeError('No storage, provide raw_dir and/or data_dir')
    return st
