import numpy as np
import matplotlib.pyplot as plt

from seismod1d.ray1d import trace, lib
from seismod1d.model import reflectivity


class Ray1D:
    def __init__(
        self,
        depth=[],
        vp=[],
        vs=[],
        rhob=[],
        delta=[],
        epsilon=[],
        gamma=[],
        theta_in=np.arange(90),
        method="isotropic",
    ):

        # layered model
        self.depth = depth
        self.vp = vp
        self.vs = vs
        self.rhob = rhob
        self.delta = delta
        self.epsilon = epsilon
        self.gamma = gamma

        # matrices with raytracer result
        self.offset = np.empty(0).astype("complex")
        self.time = np.empty(0).astype("complex")
        self.phase_angle = np.empty(0).astype("complex")
        self.group_angle = np.empty(0).astype("complex")
        self.phase_velocity = np.empty(0).astype("complex")
        self.group_velocity = np.empty(0).astype("complex")
        self.ref_coef = np.empty(0).astype("complex")

        # additional parameters
        self.theta_in = theta_in
        self.method = method

    def run_raytracer(self):

        # get input parameters
        depth = self.depth
        vp = self.vp
        vs = self.vs
        delta = self.delta
        epsilon = self.epsilon

        # avoid zero vs
        vs[vs == 0] = 1e-12

        # run raytracer
        # print('Running raytracer 1D, method: ' + self.method + ' ...')
        if self.method == "isotropic":
            (
                offset,
                time,
                phase_angle,
                group_angle,
                phase_velocity,
                group_velocity,
            ) = trace.iso(depth, vp, theta_in=self.theta_in)
        elif self.method == "vti":
            (
                offset,
                time,
                phase_angle,
                group_angle,
                phase_velocity,
                group_velocity,
            ) = trace.vti(depth, vp, vs, delta, epsilon, theta_in=self.theta_in)
        # print('...done')

        # assign output
        self.offset = offset
        self.time = time
        self.phase_angle = phase_angle
        self.group_angle = group_angle
        self.phase_velocity = phase_velocity
        self.group_velocity = group_velocity

    def resample_offset(self, offset_out):

        # resample raytracer to uniform offset sampling
        self.time = lib.resample_offset_single(self.offset, self.time, offset_out)
        self.phase_angle = lib.resample_offset_single(
            self.offset, self.phase_angle, offset_out
        )
        self.group_angle = lib.resample_offset_single(
            self.offset, self.group_angle, offset_out
        )
        self.phase_velocity = lib.resample_offset_single(
            self.offset, self.phase_velocity, offset_out
        )
        self.group_velocity = lib.resample_offset_single(
            self.offset, self.group_velocity, offset_out
        )
        self.ref_coef = lib.resample_offset_single(
            self.offset, self.ref_coef, offset_out
        )
        self.offset = np.tile(offset_out, (self.offset.shape[0], 1))

    def get_reflectivity(self, ref_method="isotropic", apply_tr_loss=False):

        # get reflectivity
        self.ref_coef = reflectivity.multi_layer(
            self.phase_angle,
            self.vp,
            self.vs,
            self.rhob,
            delta=self.delta,
            epsilon=self.epsilon,
            gamma=self.gamma,
            ref_method=ref_method,
            apply_tr_loss=apply_tr_loss
        )

    def display_raytracer(self):

        # define log types
        offset = self.offset
        time = self.time

        # get input size
        nlayers, nrays = offset.shape

        # make figure
        fig = plt.figure("Raytracer display")
        fig.clf()
        nsub = 1
        isub = 1

        # raytracer display
        plt.subplot(1, nsub, isub)
        isub = isub + 1

        # loop through layers and plot
        for ii in np.arange(nlayers):

            # get plot vectors
            xx = offset[ii, :]
            tt = time[ii, :]

            # plot
            plt.plot(xx, tt, ".-b")

        plt.grid()
        plt.xlabel("offset (m)")
        plt.ylabel("time (s)")
        plt.gca().invert_yaxis()

        # make additional figure
        fig = plt.figure("Raytracer display 2 ", figsize=(12, 12))
        fig.clf()
        nrow = 2
        ncol = 5
        isub = 1
        cmap = "gist_rainbow"
        vel_min = 0  # np.nanmin(self.phase_velocity)
        vel_max = self.phase_velocity[-1, 0]

        # time
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            self.time,
            vmin=0,
            vmax=np.nanmax(self.time[-1, :]),
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("time (s)")
        fig.colorbar(im, ax=plt.gca())

        # offset
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            self.offset,
            vmin=0,
            vmax=np.nanmax(self.offset[-1, :]),
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("offset (m)")
        fig.colorbar(im, ax=plt.gca())

        # phase angles
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.phase_angle),
            vmin=0,
            vmax=90,
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("phase_angle (deg)")
        fig.colorbar(im, ax=plt.gca())

        # group angles
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.group_angle),
            vmin=0,
            vmax=90,
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("group_angle (deg)")
        fig.colorbar(im, ax=plt.gca())

        # difference phase vs group angles
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.group_angle - self.phase_angle),
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("group_angle - phase_angle")
        fig.colorbar(im, ax=plt.gca())

        # RC
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        cr = 0.2
        if len(self.ref_coef) > 0:
            im = plt.imshow(
                np.real(self.ref_coef),
                vmin=-cr,
                vmax=cr,
                cmap=cmap,
                aspect="auto",
                interpolation="none",
            )
        plt.grid()
        plt.title("RC (real)")
        fig.colorbar(im, ax=plt.gca())

        # RC
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        cr = 0.2
        if len(self.ref_coef) > 0:
            im = plt.imshow(
                np.imag(self.ref_coef),
                vmin=-cr,
                vmax=cr,
                cmap=cmap,
                aspect="auto",
                interpolation="none",
            )
        plt.grid()
        plt.title("RC (imag)")
        fig.colorbar(im, ax=plt.gca())

        # phase velocities
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.phase_velocity),
            vmin=vel_min,
            vmax=vel_max,
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("phase_velocity (m/s)")
        fig.colorbar(im, ax=plt.gca())

        # group velocities
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.group_velocity),
            vmin=vel_min,
            vmax=vel_max,
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("group_velocity (m/s)")
        fig.colorbar(im, ax=plt.gca())

        # difference phase vs group velocities
        plt.subplot(nrow, ncol, isub)
        isub = isub + 1
        im = plt.imshow(
            np.real(self.group_velocity - self.phase_velocity),
            cmap=cmap,
            aspect="auto",
            interpolation="none",
        )
        plt.grid()
        plt.title("group_velocity  - phase_velocity (m/s)")
        fig.colorbar(im, ax=plt.gca())
