import numpy as np
import bruges as br
from seismod1d.model import reflectivity_vti, reflectivity_iso  

def multi_layer(
    reflection_angles,
    vp,
    vs,
    rho,
    delta=[],
    epsilon=[],
    gamma=[],
    apply_tr_loss = False,
    ref_method="zoeppritz_rpp",
):


    """
    Return reflection coefficient matrix for multi layered 1D input model.

    Args:
        reflection_angles (ndarray): Incidence angle (degree): 1D array of length n 
        (same angles for all layers) or m x n array (different incidense angles for each layer)
        vp (ndarray): P-wave velocity (m/s); 1D array length m.
        vs (ndarray):  S-wave velocity (m/s);  1D array length m.
        rho (ndarray): Density (g/cm3); 1D array length m.
        delta (ndarray): Thomsen anisotropic delta; empty (if isotropic) or 1D array length m.
        epsilon (ndarray): Thomsen anisotropic delta; empty (if isotropic) or 1D array length m.
        gamma (ndarray): Thomsen anisotropic delta; empty (if isotropic) or 1D array length m.

    Returns:
        RC (ndarray): Reflection coefficient; 2D array of size m x n. 
        First and last row will be nan's (interface not defined).
    """

    # get reflectivity of multiple layers with different reflection angle for each interface

    # ensure positive vs
    vs[vs == 0] = 1e-12

    # get number of input layers (must be at least 2)
    nlayers = len(vp)

    # if input angles is 1D array, make 2D array (one row per interface)
    if reflection_angles.ndim == 1:

        # make 2D array with N rows (same incidence angle for all layers)
        reflection_angles = np.tile(reflection_angles, (nlayers, 1))

    # get number of unique angles
    nangles = reflection_angles.shape[1]

    # initiate output reflection coefficient 2D Array
    RC = np.ones((nlayers, nangles)) * np.nan

    # Get reflectivity of multiple layers
    if ref_method == "zoeppritz_rpp":  # isotropic

        # get isotropic reflection coefficient       
        RC = reflectivity_iso.get_zoeppritz_rpp(
            vp, vs, rho, 
            reflection_angles, apply_tr_loss = apply_tr_loss
        )
            

    elif ref_method == "vti_exact_rpp":  # anisotropic

        # get anisotropic relectivity coefficients
        RC = reflectivity_vti.get_rpp_vti(
            vp, vs, rho, delta, epsilon, gamma, 
            reflection_angles, apply_tr_loss = apply_tr_loss
        )

        
    elif ref_method == "vti_exact_rpp_diff":  # difference anisotropic vs isotropic

        # get isotropic reflection coefficient       
        RC_iso = reflectivity_iso.get_zoeppritz_rpp(
            vp, vs, rho, 
            reflection_angles, apply_tr_loss = apply_tr_loss
        )

        # get anisotropic relectivity coefficients
        RC_vti = reflectivity_vti.get_rpp_vti(
            vp, vs, rho, delta, epsilon, gamma, 
            reflection_angles, apply_tr_loss = apply_tr_loss
        )

        # difference
        RC = RC_vti - RC_iso

    # - return result
    return RC
