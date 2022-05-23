from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
from seismod1d.rockphysics import conversions


def backus_average_cij(rho_in, c11_in, c13_in, c33_in, c44_in, c66_in):

    """
    Backus (1962)
    Input must have same uniform depth sampling|

    """

    rho = np.mean(rho_in)
    c11 = np.mean(c11_in - (c13_in ** 2 / c33_in)) + (
        np.mean(c13_in / c33_in) ** 2 / np.mean(1 / c33_in)
    )
    c13 = np.mean(c13_in / c33_in) * (1 / np.mean(1 / c33_in))
    c33 = 1 / np.mean(1 / c33_in)
    c44 = 1 / np.mean(1 / c44_in)
    c66 = np.mean(c66_in)

    BackusAverage_cij = namedtuple(
        "BackusAverage_cij", ["rho", "c11", "c13", "c33", "c44", "c66"]
    )
    return BackusAverage_cij(rho, c11, c13, c33, c44, c66)


def constant_length(
    zz, vp, vs, rho, delta, epsilon, gamma, block_length=2, qc_plot=False
):

    # get number of samples per blocking length
    nz = len(zz)  # total number of samples
    dz = zz[1] - zz[0]  # assuming constant depth interval
    iz = int(np.round(block_length / dz))  # number of samples per block
    
    # add small number to vs to avoid divide by zero
    small_value = 1e-12
    vs[vs == 0] = small_value

    # convert elastic parameters to elastic moduli
    rho, c11, c13, c33, c44, c66 = conversions.conv_vti_thoms2cij(
        rho, vp, vs, delT=delta, epsT=epsilon, gamT=gamma
    )
    
    # Note: values at first depth sample are not used due to "down-to" assumption, 
    # meaning that these values are valid down to first depth sample

    # get indices of start and end of each blocks
    istart = np.arange(0, nz, iz)  + 1 # index of first sample of each block
    iend = istart[1:] - 1  # index of last sample of each block
    iend = np.append(iend, [nz - 1])  # add

    # ensure last block is not too small
    ilast = iend[-1] - istart[-1]
    if ilast < iz - 1:
        istart = np.delete(istart, -1)
        iend = np.delete(iend, -2)

    # - initiate blocks
    rho_b = np.empty(np.shape(istart))
    c11_b = np.empty(np.shape(istart))
    c13_b = np.empty(np.shape(istart))
    c33_b = np.empty(np.shape(istart))
    c44_b = np.empty(np.shape(istart))
    c66_b = np.empty(np.shape(istart))

    # loop through all data and create blocks
    for ii in range(len(istart)):

        # select indexes for selected block
        jj = np.arange(istart[ii], iend[ii] + 1)

        # perform blocking of selected block
        (
            rho_b[ii],
            c11_b[ii],
            c13_b[ii],
            c33_b[ii],
            c44_b[ii],
            c66_b[ii],
        ) = backus_average_cij(rho[jj], c11[jj], c13[jj], c33[jj], c44[jj], c66[jj])

    # convert back to Thomsen parameters
    vp_b, vs_b, del_b, eps_b, gam_b = conversions.conv_vti_cij2_thoms(
        rho_b, c11_b, c13_b, c33_b, c44_b, c66_b
    )
    
    # set vs back to zero
    vs_b[vs_b == small_value] = 0

    # output depth
    zz_b = zz[iend]

    # add top layer (elastic values not used)
    zz_b = np.insert(zz_b, 0, zz[0])
    vp_b = np.insert(vp_b, 0, vp_b[0])
    vs_b = np.insert(vs_b, 0, vs_b[0])
    rho_b = np.insert(rho_b, 0, rho_b[0])
    del_b = np.insert(del_b, 0, del_b[0])
    eps_b = np.insert(eps_b, 0, eps_b[0])
    gam_b = np.insert(gam_b, 0, gam_b[0])

    # QC plot
    if qc_plot:

        # collect data in dictionaries
        zz, vp, vs, rho, delta, epsilon, gamma
        model_input = {
            "depth": zz,
            "vp": vp,
            "vs": vs,
            "rhob": rho,
            "delta": delta,
            "epsilon": epsilon,
            "gamma": gamma,
        }
        model_backus = {
            "depth": zz_b,
            "vp": vp_b,
            "vs": vs_b,
            "rhob": rho_b,
            "delta": del_b,
            "epsilon": eps_b,
            "gamma": gam_b,
        }

        # qc plot
        backus_qc_plot(model_input, model_backus)

    return zz_b, vp_b, vs_b, rho_b, del_b, eps_b, gam_b


def backus_qc_plot(model_input, model_backus):

    # define log types
    log_types = list(model_input.keys())[1:]
    ncol = len(log_types)

    # - make figure
    fig = plt.figure("Backus QC")
    fig.clf()

    # - plot original and blocked logs
    icol = 1
    for type_s in log_types:

        plt.subplot(1, ncol, icol)
        plt.cla()
        icol = icol + 1

        plt.plot(model_input[type_s], model_input["depth"], "b-")
        plt.step(model_backus[type_s], model_backus["depth"], "r-", where="post")

        plt.grid()
        plt.title(type_s)
        plt.ylabel("DEPTH (m)")
        plt.gca().invert_yaxis()
