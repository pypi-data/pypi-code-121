import numpy as np
import pandas as pd
import time
from seismod1d.wavelet import get_wavelet
from seismod1d.model import lib, reflectivity, synthetics
from seismod1d import td
from seismod1d.rockphysics import backus
from seismod1d.ray1d.ray1d import Ray1D
from seismod1d.ray1d import nmo
from seismod1d.ray1d.lib import resample_to_uniform_offset
from seismod1d.model import reflectivity_vti, reflectivity_iso  # , reflectivity_vti_test


NSPACE = 4


class SynthModel:
    def __init__(
        self,
        depth,
        vp,
        vs,
        rhob,
        delta=[],
        epsilon=[],
        gamma=[],
        depth_top=[],
        time_top=0,
    ):

        # if top depth is defined, create top layer
        if depth_top != []:
            depth, vp, vs, rhob, delta, epsilon, gamma = lib.insert_model_top(
                depth_top, depth, vp, vs, rhob, delta, epsilon, gamma
            )

        # layered model
        self.depth = np.array(depth, dtype=np.float32)
        self.vp = np.array(vp, dtype=np.float32)
        self.vs = np.array(vs, dtype=np.float32)
        self.rhob = np.array(rhob, dtype=np.float32)
        self.delta = np.array(delta, dtype=np.float32)
        self.epsilon = np.array(epsilon, dtype=np.float32)
        self.gamma = np.array(gamma, dtype=np.float32)

        # top of model
        self.time_top = time_top
        self.time = td.get_time(self.depth, self.vp, start_time=self.time_top)

        # general model settings
        self.model_domain = "angle"  # model in angle or offset
        self.model_type = "isotropic"  # isotropic, vti
        self.model_angle = np.arange(0, 90)
        dz = 10
        self.model_offset = np.arange(0, 6000 + dz, dz)
        # self.model_offset_type = 'moveout' # moveout, nmo-corr

        # reflectivity
        self.ref_coef = np.empty(0).astype("complex")  # reflectivity coefficient
        self.ref_time = np.empty(0).astype("float")  # reflectivity time (s)

        # trace data
        self.traces = []  # 2D (N x M) array with synthetic trace data
        self.traces_time = []  # 1D array (N) with time values (uniform sampling)
        self.traces_x = []  # 1D array (M) with angle/offset values
        self.traces_depth = []  # 1D array (N) with depth values (non-uniform sampling)

        # raytracer
        self.raytracer = Ray1D()

    def precondition(self, 
                     depth_step_resample=0.1, 
                     apply_value_centering=False,
                     depth_crop_after_centering=False,
                     apply_depth_resample=True,
                     apply_backus=True,
                     merge_layers=True,
                     backus_step=2, 
                     backus_qc_plot=False,                     
                     ):

        # measure time
        start_time = time.time()        

        # remove leading/trailing nan's
        print("Removing leading/trailing nan values ...")
        (
            self.depth,
            self.vp,
            self.vs,
            self.rhob,
            self.delta,
            self.epsilon,
            self.gamma,
        ) = lib.remove_nan(
            self.depth,
            self.vp,
            self.vs,
            self.rhob,
            self.delta,
            self.epsilon,
            self.gamma,
        )        

        # adjust depth from centered to down-to definition
        if apply_value_centering:
            print("Adjusting depths from centered definition to layered (down-to)...")
            if depth_crop_after_centering:
                self.depth = lib.depth_centre_to_layer(self.depth, z_base=self.depth[-1])
            else:
                self.depth = lib.depth_centre_to_layer(self.depth)

        # resample to uniform depth sampling
        if apply_depth_resample:
            print("Resampling to uniform depth sampling (dz = " + str(depth_step_resample) + ")...")
            (
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
            ) = lib.depth_resample(
                depth_step_resample,
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
            )                    

        # backus blocking
        if apply_backus: 
            print("Backus blocking...")
            start_time = time.time()
            (
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
            ) = backus.constant_length(
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
                block_length=backus_step,
                qc_plot=backus_qc_plot,
            )
            print(
                "...done. Time elapsed backus: "
                + "{:.3f}".format(time.time() - start_time)
                + " s"
            )    
            
        # merge layers with identical elastic parameters
        if merge_layers:
            print("Merging identical layers ...")            
            (
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
            ) = lib.merge_layers(                
                self.depth,
                self.vp,
                self.vs,
                self.rhob,
                self.delta,
                self.epsilon,
                self.gamma,
            )                               

        # recalculate model time
        self.time = td.get_time(self.depth, self.vp, start_time=self.time_top)

    def info(self):

        # add to pandas dataframe and print header
        df = pd.DataFrame(
            {"DEPTH": self.depth, "VP": self.vp, "VS": self.vs, "RHOB": self.rhob}
        )

        # add VTI anisotropy columns
        (nval, ncol) = df.shape
        if len(self.delta) == 0:
            self.delta = np.zeros(nval)
        if len(self.epsilon) == 0:
            self.epsilon = np.zeros(nval)
        if len(self.gamma) == 0:
            self.gamma = np.zeros(nval)

        df["DEL"] = self.delta
        df["EPS"] = self.epsilon
        df["GAM"] = self.gamma

        print(df.head())
        print(df.tail())

    def get_reflectivity(self, apply_tr_loss = False, raytracer_angles=np.arange(0, 90)):

        # determine reflection and raytracer calculation method
        if self.model_type == "isotropic":
            ray_method = "isotropic"
            ref_method = "zoeppritz_rpp"
        elif self.model_type == "vti":
            ray_method = "vti"
            ref_method = "vti_exact_rpp"

        # get reflection times
        if self.model_domain == "angle":  # angle domain output (AVA-modelling)

            # get reflectivity
            print("Get reflectivity of all layers: " + ref_method + "...")
            start_time = time.time()
            self.ref_coef = reflectivity.multi_layer(
                self.model_angle,
                self.vp,
                self.vs,
                self.rhob,
                delta=self.delta,
                epsilon=self.epsilon,
                gamma=self.gamma,
                ref_method=ref_method,
                apply_tr_loss=apply_tr_loss,
            )
            print(
                "...done. Time elapsed, reflectivity: "
                + "{:.3f}".format(time.time() - start_time)
                + " s"
            )

            # get reflectivity time (zero-offset time from model)
            tv = self.time

            # make 2D array of reflection time
            self.ref_time = np.tile(
                tv.reshape(tv.shape[0], 1), (1, self.ref_coef.shape[1])
            )

            # set model x
            self.traces_x = self.model_angle

        elif self.model_domain == "offset":  # angle domain output (AVA-modelling)

            # run raytracer
            print("Running raytracer: " + ray_method + "...")
            start_time = time.time()
            self.raytracer = Ray1D(
                depth=self.depth,
                vp=self.vp,
                vs=self.vs,
                rhob=self.rhob,
                delta=self.delta,
                epsilon=self.epsilon,
                gamma=self.gamma,
                theta_in=raytracer_angles,
                method=ray_method,
            )
            self.raytracer.run_raytracer()
            print(
                "...done. Time elapsed, raytracer: "
                + "{:.3f}".format(time.time() - start_time)
                + " s"
            )

            # get reflectivity (added to raytracer)
            print("Get reflectivity of all layers: " + ref_method + "...")
            start_time = time.time()
            self.raytracer.get_reflectivity(ref_method=ref_method, apply_tr_loss=apply_tr_loss)
            print(
                "...done. Time elapsed, reflectivity: "
                + "{:.3f}".format(time.time() - start_time)
                + " s"
            )

            # resample reflectivity to uniform offset
            self.ref_coef = resample_to_uniform_offset(
                self.raytracer.offset, self.raytracer.ref_coef, self.model_offset
            )
            self.ref_time = resample_to_uniform_offset(
                self.raytracer.offset, self.raytracer.time, self.model_offset
            )

            # assign to model
            self.traces_x = self.model_offset

    def get_traces(
        self,
        wav_time=[],
        wav_amp=[],
        wav_dt=0.004,        
        time_min=[],
        time_max=[],        
        apply_nmo_stretch=False,
        apply_td_stretch=False,
        td_depth=[],
        td_time=[],
    ):

        # measure time
        start_time = time.time()

        # get default wavelet if empty
        if len(wav_time) == 0:
            print("Get default wavelet...")
            wav_time, wav_amp, wav_name = get_wavelet(wav_dt=wav_dt)

        # apply nmo stretch only in offset domain
        if self.model_domain == "angle":
            apply_nmo_stretch = False

        # if NMO is to be applied later, recalculate moveout curves upfront using NMO method (not raytracer)
        # this ensures event flatness as raytracer and NMO correction movout might differ slightly
        if apply_nmo_stretch:
            print("Recalculating moveout curves...")

            # establish temporary time-depth trend to use for NMO moveout estimation
            dt = wav_time[1] - wav_time[0]
            tv = np.arange(self.time[0], self.time[-1] + dt, dt)
            zv = td.get_depth_from_td(
                self.depth, self.time, tv, kind="interp", int_method="linear"
            )

            # get reflection time from NMO method
            self.ref_time = nmo.get(
                tv,
                zv,
                self.traces_x,
                self.depth,
                self.vs,
                self.delta,
                self.epsilon,
                nmo_type=self.model_type,
                tv_output=self.time,
                direction=1,
                nterm=4,
            )

        # apply td stretch prior to convolution with wavelet
        if apply_td_stretch:
            print("Applying TD stretch......")
            self.ref_time = td.apply_td_stretch(
                self.ref_time, self.depth, self.time, td_depth, td_time
            )

        # convolve with wavelet to make traces
        print("Making traces (convolution with wavelet)...")
        self.traces, self.traces_time = synthetics.make_traces(
            self.ref_time,
            self.ref_coef,
            wav_time,
            wav_amp,
            tmin=time_min,
            tmax=time_max,
        )
        print(
            "...done. Time elapsed, make traces: "
            + "{:.3f}".format(time.time() - start_time)
            + " s"
        )

        # apply NMO stretch
        if apply_nmo_stretch:
            print("Applying NMO stretch.....")

            # get depth at trace time
            zv = td.get_depth_from_td(
                self.depth,
                self.time,
                self.traces_time,
                kind="interp",
                int_method="linear",
            )

            # get reflection time from NMO method
            TX = nmo.get(
                self.traces_time,
                zv,
                self.traces_x,
                self.depth,
                self.vs,
                self.delta,
                self.epsilon,
                nmo_type=self.model_type,
                direction=1,
                nterm=4,
            )

            # apply td stretch
            if apply_td_stretch:

                # update nmo traveltime matrix according to td-stretch
                TX = td.apply_td_stretch(
                    TX, self.depth, self.time, td_depth, td_time
                )  # , direction = 1)
                TX = nmo.resample_tx(TX, self.traces_time)

            # apply NMO correction
            self.traces = nmo.apply_tx(self.traces, self.traces_time, TX)
            print("...done")

    def display_traces(self, xlim=[], ylim=[]):

        # make xlabel
        xlabel = "Angle (deg)"
        if self.model_domain == "offset":
            xlabel = "Offset (m)"

        # show traces
        synthetics.display_traces(
            self.traces_x,
            self.traces_time,
            self.traces,
            xlim=xlim,
            ylim=ylim,
            xlabel=xlabel,
        )
