

from . import io

targets = io.get_target_data()


def run_snid(filepath,
             lbda_range=[4000,9000],
             delta_redshift=0.05, verbose=False,
             **kwargs):
    """ """
    from .spectroscopy import Spectrum
    spec = Spectrum.from_filename(filepath)
    t0, z = targets.loc[spec.targetname][["t0","redshift"]].values
    phase = spec.get_phase(t0, z=z)
    #if redshift quality is 2, delta_Redshift could be reduced
    return spec.fit_snid(phase=phase, lbda_range=lbda_range, 
                         redshift=z, delta_redshift=delta_redshift,
                         verbose=verbose, **kwargs)
