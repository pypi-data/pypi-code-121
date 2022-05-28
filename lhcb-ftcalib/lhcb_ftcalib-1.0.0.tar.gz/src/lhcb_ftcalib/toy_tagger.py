import os
import pickle
import numpy as np
import pandas as pd

np.random.seed(384994875)


class ToyDataGenerator:
    def __init__(self):
        pass

    def __decay_time_generator(self, chunk, lifetime):
        # Returns decay time distribution with arctan acceptance model
        while True:
            tau = np.random.exponential(scale = 1.0 / lifetime, size=chunk)
            tau_choose  = np.random.uniform(0, 1, chunk)
            tau = tau[tau_choose < 2 * np.arctan(2 * tau) / np.pi]
            yield tau

    def __mistag_distribution(self, Npos, Nneg, tagger_type, func, params):
        # Draw random mistag values from pre-sampled distributions
        # These distributions were sampled for positive and negative tag decisions

        def smear(distr, binwidth):
            # Add noise to sampled values so that they are uniformly distributed between bins
            N = len(distr)
            smear = np.random.uniform(-binwidth / 2, binwidth / 2, size=N)
            distr += smear
            distr[distr > 0.5] -= 0.5
            return distr

        taghists = pickle.load(open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "tagger_distributions.dict"), "rb"))

        histbins      = taghists["nbins"]
        histcenters   = taghists["centers"]
        dist_pos      = taghists[tagger_type][1]["bins"]
        dist_neg      = taghists[tagger_type][-1]["bins"]
        p_density_pos = dist_pos / (2 * histbins)
        p_density_neg = dist_neg / (2 * histbins)

        # Generate raw eta distributions
        eta_plus  = smear(np.random.choice(histcenters, size=Npos, p=p_density_pos), 0.5 / histbins)
        eta_minus = smear(np.random.choice(histcenters, size=Nneg, p=p_density_neg), 0.5 / histbins)

        # omega distribution can exceed 0.5. This does not make sense but it
        # can happen for a given calibration function. By default the toy
        # generator should scale the eta distribution so that the calibrated
        # mistag does not exceed 0.5. The same could happen for omega < 0 which
        # are equally nonsensical, but those values can be forced to be
        # perfectly tagged.
        func.init_basis(eta_plus)
        omega_plus  = func.eval(params, eta_plus,  +np.ones(Npos))
        omega_minus = func.eval(params, eta_minus, -np.ones(Nneg))

        def rescale(eta, omega):
            omega_max = omega.max()
            if omega_max <= 0.5:
                # All good
                return eta

            # Rescale eta so that omega stays in range
            eta_critical = eta[np.argmin(np.abs(omega - 0.5))] - 1e-2

            eta_max = eta.max()
            eta *= eta_critical / eta_max
            return eta

        eta_plus  = rescale(eta_plus,  omega_plus)
        eta_minus = rescale(eta_minus, omega_minus)

        return eta_plus, eta_minus

    def __call__(self, N, func, params, osc, tagger_types, lifetime=1.52, DM=0.5065, DG=0, Aprod=0, tag_effs=None):
        r"""
        Call of toy data generator functor.

        :param N: Number of events to generate
        :type N: int
        :param func: Calibration function
        :type func: CalibrationFunction
        :param params: List of calibration parameters set in flavour convention for each tagger.
        :type params: list of list
        :param osc: If true, will simulate B oscillation
        :type osc: bool
        :param tagger_types: Pre-sampled distribution to use. One of ["SSKaon", "SSproton", "SSPion", "OSElectron", "VtxCh", "OSMuon", "OSCharm", "OSKaon"]
        :type tagger_types: list of str
        :param lifetime: B meson lifetime
        :type lifetime: float
        :param DM: :math:`\Delta m`
        :type DM: float
        :param DG: :math:`\Delta\Gamma`
        :type DG: float
        :param Arod: Production asymmetry
        :type Arod: float
        :param tag_effs: List of tagging efficiencies. Default: 100% for each tagger
        :type tag_effs: list of float or None
        """
        Nplus  = int(N * 0.5 * (1 + Aprod))

        df = pd.DataFrame({"FLAV_PROD" : np.ones(N, dtype=np.int32)})
        df.loc[Nplus:, "FLAV_PROD"] *= -1
        df.eval("FLAV_DECAY=FLAV_PROD", inplace=True)

        if osc:
            # Generate decay time distribution
            tau_gen = self.__decay_time_generator(N, lifetime)
            tau = next(tau_gen)
            while len(tau) < N:
                tau = np.append(tau, next(self.__decay_time_generator(N, lifetime)))
            tau = tau[:N]
            df["TAU"] = tau

            # Oscillate mesons by inverting decay flavour if oscillation is likely
            # This way, there is a time oscillation for prod!=pred and prod!=pred
            Amix = np.cos(DM * df.TAU) / np.cosh(0.5 * DG * df.TAU)
            osc_prob = 0.5 * (1 - Amix)
            rand = np.random.uniform(0, 1, N)
            has_oscillated = rand < osc_prob
            df.loc[has_oscillated, "FLAV_DECAY"] *= -1

            # Compute predicted flavour
            df.eval("FLAV_PRED=FLAV_DECAY", inplace=True)
            df.loc[np.sign(Amix) == -1, "FLAV_PRED"] *= -1

            df["OSC"] = has_oscillated
        else:
            df.eval("FLAV_PRED=FLAV_DECAY", inplace=True)

        # Simulate tagging
        for t, tparams in enumerate(params):
            name = f"TOY{t}"
            dec_branch = f"{name}_DEC"
            eta_branch = f"{name}_ETA"
            omg_branch = f"{name}_OMEGA"

            # Compute mistag distribution eta
            df.eval(f"{dec_branch}=FLAV_PROD", inplace=True)  # perfect tagging
            eta_plus, eta_minus = self.__mistag_distribution(Npos = (df[dec_branch] == +1).sum(),
                                                             Nneg = (df[dec_branch] == -1).sum(),
                                                             tagger_type = tagger_types[t],
                                                             func        = func,
                                                             params      = tparams)
            df.eval(f"{eta_branch} = 0.5", inplace=True)
            df.loc[df[dec_branch] == +1, eta_branch] = eta_plus
            df.loc[df[dec_branch] == -1, eta_branch] = eta_minus

            # Test monotonicity (which is an assumpting we make here)
            lineshape_plus = func.eval(tparams, np.linspace(0.001, 0.5, 1000), np.ones(1000))
            lineshape_minus = func.eval(tparams, np.linspace(0.001, 0.5, 1000), -np.ones(1000))
            if not np.all(np.diff(lineshape_plus) >= 0) or not np.all(np.diff(lineshape_minus) >= 0):
                print(f"Toy warning: Calibration function is not monotonic for parameters {tparams} -> Abort")
                return None

            # Calibrate mistag distribution
            # func.init_basis(df[eta_branch])
            df[omg_branch] = func.eval(tparams, df[eta_branch], df[dec_branch])

            Noverflow = (df[omg_branch] > 0.5).sum()
            if Noverflow > 0:
                print(f"Toy warning: {Noverflow} calibrated mistags still exceed 0.5"
                      f"with a maximum at {df.loc[df[omg_branch] > 0.5, omg_branch].max()}."
                       "Make sure calibration function is monotone! Will force those values to 0.5")
                df.loc[df[omg_branch] >= 0.5, dec_branch] = 0
                df.loc[df[omg_branch] >= 0.5, omg_branch] = 0.5
            df.loc[df[omg_branch] < 0, omg_branch] = 0  # Underflow

            # Simulate tagging decisions (this is where the magic happens and
            # the calibration parameters are encoded into the (eta, dec)
            # information)
            rand = np.random.uniform(0, 1, N)
            df.loc[df[omg_branch] > rand, dec_branch] *= -1

        df = df.sample(frac=1)
        df.reset_index(drop=True, inplace=True)

        if tag_effs is not None:
            assert len(tag_effs) == len(tagger_types)
            for i, tag_eff in enumerate(tag_effs):
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_OMEGA"] = 0.5
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_ETA"] = 0.5
                df.loc[int(tag_eff * len(df)):, f"TOY{i}_DEC"] = 0

            df = df.sample(frac=1)
            df.reset_index(drop=True, inplace=True)

        df["eventNumber"] = np.arange(len(df))
        return df
