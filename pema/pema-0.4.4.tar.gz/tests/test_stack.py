import straxen
import pema
import wfsim
import time
import matplotlib.pyplot as plt
import strax
import tempfile
import os
import unittest
import shutil
import uuid
import numpy as np

straxen.print_versions(['strax', 'straxen', 'wfsim', 'nestpy', 'pema'])

run_id = '008000'


@unittest.skipIf(not straxen.utilix_is_configured(), "No db access, cannot test!")
class TestStack(unittest.TestCase):
    """
    Test the entire chain, from simulation to plotting the results

    Note:
        Important to notice is that despite this being slightly bad practice,
        the tests are ordered. This allows for speadier testing since we need
        to have some data to work with. Since that takes a while, we have
        decided to re-use the data.
    """

    @classmethod
    def setUpClass(cls):
        cls.set_temporary_test_folder()
        cls.set_script()

    @classmethod
    def set_temporary_test_folder(cls):
        temp_folder = uuid.uuid4().hex
        cls.tempdir = os.path.join(tempfile.gettempdir(), temp_folder)
        os.mkdir(cls.tempdir)

    @classmethod
    def set_script(cls):
        if not straxen.utilix_is_configured():
            return
        # setting up instructions like this may take a while. You can set e.g.
        instructions = dict(
            event_rate=50,  # Don't make too large -> overlapping truth info
            chunk_size=1,  # keep large -> less overhead but takes more RAM
            n_chunk=2,
            tpc_radius=straxen.tpc_r,
            tpc_length=straxen.tpc_z,
            drift_field=200,  # kV/cm
            energy_range=[2, 10],  # keV
            nest_inst_types=wfsim.NestId.ER,
        )
        temp_dir = cls.tempdir
        instructions_csv = os.path.join(temp_dir, 'inst.csv')

        pema.inst_to_csv(
            instructions_csv,
            get_inst_from=pema.rand_instructions,
            **instructions)

        config_update = {
            "detector": 'XENONnT',
            "fax_file": os.path.abspath(instructions_csv),
            "cmt_run_id_sim": run_id,
        }

        print("Temporary directory is ", temp_dir)
        os.chdir(temp_dir)

        st = pema.pema_context(fax_config='fax_config_nt_sr0_v0.json',
                               cmt_run_id_sim=run_id,
                               base_dir=temp_dir,
                               raw_dir=temp_dir,
                               data_dir=temp_dir,
                               config_update=config_update,
                               )
        st.set_context_config(
            {'allow_shm': True,
             'allow_lazy': False,
             'timeout': 300,
             'max_messages': 10,
             }
        )
        script_writer = pema.ProcessRun(st, run_id,
                                        ('raw_records',
                                         'records',
                                         'peaklets',
                                         'truth_matched',
                                         'match_acceptance_extended'
                                         ))
        cls.script = script_writer

    def test_first_run_execute(self):
        print(f'Start script - context hash {self.script.st._context_hash()}')
        cmd, name = self.script.make_cmd()
        for t in self.script.target:
            self.script.st.make(self.script.run_id[0], t)
        self.script.exec_local(cmd, name)

        print(f'Starting\n\t{cmd}')
        t0 = time.time()
        print(self.script.process.communicate())
        print(f'took {time.time() - t0:.2f}s')
        print(f'Script done- context hash {self.script.st._context_hash()}')
        time.sleep(3)

        print(f'Done')
        print(f'Stored: {self.script.all_stored(show_key=True)}')
        check_all_stored = self.script.all_stored(return_bool=True)
        check_log_file = os.path.exists(self.script.log_file)
        try:
            check_did_finish = self.script.job_finished()
        except pema.scripts.JobFailedError:
            check_did_finish = False
        if not (check_all_stored and check_log_file and check_did_finish):
            print(f'Failed: '
                  f'check_all_stored {check_all_stored}, '
                  f'check_log_file: {check_log_file}, '
                  f'check_did_finish: {check_did_finish}, '
                  )
            if check_log_file:
                print(self.script.read_log())
            raise pema.scripts.JobFailedError(f'Job did not finish')

    def test_first_run_plugins(self):
        self.script.purge_below('match_acceptance_extended')
        for t in strax.to_str_tuple(self.script.target):
            for r in strax.to_str_tuple(self.script.run_id):
                if (self.script.st.get_save_when(t) > strax.SaveWhen.NEVER):
                    self.script.st.make(r, t)
                    assert self.script.st.is_stored(r, t)

    def test_next_print(self):
        print(self.script)

    def test_next_make_dali_script(self):
        # Just make sure we write some file, we are not actually going
        # to run it
        self.script.exec_dali('ls', 'test_job', 'dummy_activate')
        assert os.path.exists(self.script.script_file)

    def test_later_compare(self):
        st = self.script.st
        st2 = st.new_context()
        for t in strax.to_str_tuple(self.script.target):
            print(run_id, t)
            st2.make(run_id, t)
        peaks_1 = st.get_array(run_id, 'match_acceptance_extended')
        peaks_2 = st2.get_array(run_id, 'match_acceptance_extended')
        if 'run_id' not in peaks_1.dtype.names:
            peaks_1 = pema.append_fields(peaks_1, 'run_id', [run_id] * len(peaks_1))
            peaks_2 = pema.append_fields(peaks_2, 'run_id', [run_id] * len(peaks_2))
        pema.compare_truth_and_outcome(
            st, peaks_1,
            max_peaks=2,
            show=False,
            fig_dir=self.tempdir,
            raw=True
        )
        plt.clf()
        pema.compare_outcomes(st, peaks_1,
                              st2, peaks_2,
                              max_peaks=2,
                              show=False,
                              different_by=None,
                              fig_dir=self.tempdir,
                              raw=False,
                              )
        plt.clf()
        if len(peaks_1):
            pema.summary_plots.plot_peak_matching_histogram(
                peaks_1,
                'n_photon',
                bin_edges=[0, int(peaks_1['n_photon'].max())]
            )
            plt.clf()
            pema.summary_plots.acceptance_plot(
                peaks_1,
                'n_photon',
                bin_edges=[0, int(peaks_1['n_photon'].max())]
            )
            plt.clf()

    def test_later_make_ev_matched(self):
        st = self.script.st
        st.get_array(run_id, 'truth_events')

    def test_later_rec_bas(self):
        st = self.script.st
        st2 = st.new_context()
        peaks_1 = st.get_array(run_id, 'match_acceptance_extended')
        peaks_2 = st2.get_array(run_id, 'match_acceptance_extended')
        peaks_1_kwargs = dict(bins=10)
        if len(peaks_1):
            pema.summary_plots.rec_plot(peaks_1, **peaks_1_kwargs)
            pema.summary_plots.reconstruction_bias(peaks_1, s1_kwargs=peaks_1_kwargs)
            plt.clf()
        if len(peaks_1) and len(peaks_2):
            if not np.sum(peaks_1['type'] == 1):
                return
            pema.summary_plots.rec_diff(
                peaks_1,
                peaks_2,
                s1_kwargs=peaks_1_kwargs,
                s2_kwargs=peaks_1_kwargs,
            )
            plt.clf()

    def test_later_inst_plot(self):
        st = self.script.st
        peaks = st.get_array(run_id, ('peaks', 'peak_basics'))
        st.plot_peaks(run_id, time_within=peaks[0])
        plt.clf()
        st.plot_peaks(run_id, time_within=peaks[0], xaxis='since_start')
        pema.plot_peak(peaks[0], t0=None)
        plt.clf()

        st.plot_peaks(run_id, time_within=peaks[0], xaxis=False)
        pema.save_canvas('test_fig', os.path.join(self.tempdir, 'figs'), tight_layout=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)
