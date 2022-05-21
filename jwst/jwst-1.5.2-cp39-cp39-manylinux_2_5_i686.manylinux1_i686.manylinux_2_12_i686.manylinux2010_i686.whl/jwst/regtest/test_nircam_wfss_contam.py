"""Regression test for WFSS contam correction of NIRCam data"""
import pytest

from jwst.regtest import regtestdata as rt


@pytest.fixture(scope='module')
def run_wfss_contam(jail, rtdata_module):
    """Run the wfss_contam step"""
    rtdata = rtdata_module

    # Get input data files
    rtdata.get_data('nircam/wfss/jw01076_nircam_f322w2_i2d.fits')
    rtdata.get_data('nircam/wfss/jw01076_nircam_f322w2_segm.fits')
    rtdata.get_data('nircam/wfss/jw01076003001_01101_00001_nrca5_srctype.fits')

    # Run the step
    step_params = {
        'step': 'jwst.wfss_contam.WfssContamStep',
        'args': [
            '--save_simulated_image=True',
            '--save_contam_images=True',
            '--skip=False',
        ]
    }
    rtdata = rt.run_step_from_dict(rtdata, **step_params)
    return rtdata


@pytest.mark.bigdata
@pytest.mark.parametrize(
    'suffix',
    ['simul', 'contam', 'wfsscontamstep']
)
def test_nrc_wfss_contam(run_wfss_contam, fitsdiff_default_kwargs, suffix):
    """Regression test for wfss_contam applied to NIRCam WFSS data"""
    rt.is_like_truth(
        run_wfss_contam, fitsdiff_default_kwargs, suffix, 'truth/test_nircam_wfss_contam'
    )
