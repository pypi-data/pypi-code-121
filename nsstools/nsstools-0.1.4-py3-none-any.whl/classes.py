# -*- coding: utf-8 -*-

"""NssStar
:author Jean-Louis Halbwachs, Carine Babusiaux, Nicolas Leclerc
:id $Id: classes.py 745453 2022-04-22 15:37:51Z nleclerc $
"""

import pandas as pd
import numpy as np


class NssSource(object):

    def __init__(self, star: pd.DataFrame, indice=0):
        self._star = star.iloc[indice]
        self._cormat = self._correlation_matrice()
        values_names, errors_names = self._fields()
        self._values_names = [x for x in values_names if np.isfinite(self._star["{}_error".format(x)])]
        self._errors = [self._star[x] for x in errors_names if np.isfinite(self._star[x])]

    def _correlation_matrice(self):
        mat = np.fromstring(self._star["corr_vec"][1:-1], dtype=float, sep=',')
        return mat[np.isfinite(mat) & (mat != 0.)]

    def _fields(self):
        base = ["ra", "dec", "parallax", "pmra", "pmdec",
                               "a_thiele_innes", "b_thiele_innes", "f_thiele_innes",
                               "g_thiele_innes", "c_thiele_innes", "h_thiele_innes"]

        star_type = self._star["nss_solution_type"]
        if star_type == "Orbital":
            values_names = base + ["eccentricity", "period", "t_periastron"]
        elif "OrbitalAlternative" in star_type or "OrbitalTargetedSearch" in star_type:
            values_names = base + ["period", "eccentricity", "t_periastron"]
        elif star_type.startswith("SB"):
            values_names = base + ["period", "center_of_mass_velocity",
                             "semi_amplitude_primary", "semi_amplitude_secondary", "eccentricity",
                             "arg_periastron", "t_periastron"]
        elif star_type == "AstroSpectroSB1":
            values_names = base + ["center_of_mass_velocity",
                             "eccentricity", "period", "t_periastron"]
        elif star_type.startswith("Eclipsing"):
            values_names = base + ["t_periastron", "center_of_mass_velocity",
                             "semi_amplitude_primary", "semi_amplitude_secondary",
                             "mass_ratio", "fill_factor_primary", "fill_factor_secondary",
                             "eccentricity", "inclination", "arg_periastron", "temperature_ratio"]
        elif "Acceleration" in star_type:
            values_names = ["ra","dec","parallax","pmra","pmdec","accel_ra","accel_dec","deriv_accel_ra","deriv_accel_dec"]
        elif "TrendSB1" in star_type:
            values_names = ["mean_velocity","first_deriv_velocity","second_deriv_velocity"]
        elif "VIMF" in star_type:
            values_names = ["ra","dec","parallax","pmra","pmdec","vim_d_ra","vim_d_dec"]
        else:
            raise ValueError("Uknown start type {}".format(star_type))

        errors_names = ["{}_error".format(n) for n in values_names]

        return values_names, errors_names

    def covmat(self):
        len_err = len(self._errors)

        if len(self._cormat) != len_err * ((len_err - 1) / 2):
            raise ValueError("Errors size {} and Cormat size {} are not compatible".format(len_err, len(self._cormat)))

        covmat = np.empty([len_err, len_err])
        k = 0
        for j in range(len_err):
            covmat[j, j] = self._errors[j] ** 2
            for i in range(j):
                covmat[i, j] = self._cormat[k] * self._errors[i] * self._errors[j]
                covmat[j, i] = covmat[i, j]
                k += 1

        return pd.DataFrame(data=covmat, index=self._values_names, columns=self._values_names)

    # From Jean-Louis Halbwachs Fortran code 
    def _TICH_errors(self, covMat, A, B, F, G, C, H):
        # calcul de omega + Omega
        wpOme = np.arctan2(B - F, A + G)
        # calcul de omega - Omega
        wmOme = np.arctan2(-B - F, A - G)
        # Premieres estimations entre -pi et +pi
        w = (wpOme + wmOme) / 2.
        Ome = (wpOme - wmOme) / 2.

        # Omega doit etre entre 0 et pi; on ajoute donc 2 pi
        if Ome < 0:
            # a wpOme, ou on en retranche autant a wmOme.
            Ome += np.pi
            # Correction de w en consequence.
            w += np.pi

        # Recadrage de w entre 0 et 2 pi.
        if w > 2 * np.pi:
            w -= 2 * np.pi
        elif w < 0:
            w += 2 * np.pi

        ApG2pBmF2 = (A+G)**2 + (B-F)**2
        GmA2pBpF2 = (G-A)**2 + (B+F)**2

        # Coef. devant dA
        tAw = (F-B)/ApG2pBmF2 + (B+F)/GmA2pBpF2
        tAO = (F-B)/ApG2pBmF2 - (B+F)/GmA2pBpF2
        # Coef. devant dB
        tBw = (A+G)/ApG2pBmF2 + (G-A)/GmA2pBpF2
        tBO = (A+G)/ApG2pBmF2 - (G-A)/GmA2pBpF2
        # Coef. devant dF
        tFw = -(A+G)/ApG2pBmF2 + (G-A)/GmA2pBpF2
        tFO = -(A+G)/ApG2pBmF2 - (G-A)/GmA2pBpF2
        # Coef. devant dG
        tGw = (F-B)/ApG2pBmF2 - (B+F)/GmA2pBpF2
        tGO = (F-B)/ApG2pBmF2 + (B+F)/GmA2pBpF2

        sigw = np.sqrt(tAw*tAw*covMat[0, 0] + tBw*tBw*covMat[1, 1] + tFw*tFw*covMat[2, 2] + tGw*tGw*covMat[3, 3]
                       + 2.0 * (tAw*tBw*covMat[0, 1] + tAw*tFw*covMat[0, 2] + tBw*tFw*covMat[1, 2]
                                + tAw*tGw*covMat[0, 3] + tBw*tGw*covMat[1, 3] + tFw*tGw*covMat[2, 3])) / 2.0

        sigOme = np.sqrt(tAO*tAO*covMat[0, 0] + tBO*tBO*covMat[1, 1] + tFO*tFO*covMat[2, 2] + tGO*tGO*covMat[3, 3]
                         + 2.0 * (tAO*tBO*covMat[0, 1] + tAO*tFO*covMat[0, 2] + tAO*tGO*covMat[0, 3]
                                  + tBO*tFO*covMat[1, 2] + tBO*tGO*covMat[1, 3] + tFO*tGO*covMat[2, 3])) / 2.0

        # Calcul des denominateurs des deux
        tg2iAG = np.abs((A + G) * np.cos(wmOme))
        # formules donnant tan^2 i/2
        tg2iBF = np.abs((F - B) * np.sin(wmOme))
        # Termes de calcul de l'incertitude
        sinOcosO = np.sin(Ome)*np.cos(Ome)
        sinwcosw = np.sin(w)*np.cos(w)

        # Choix de la formule de plus grand denominateur
        sigincl = np.nan
        siga1 = np.nan

        if tg2iAG > tg2iBF:
            # Calcul de i
            incl = 2. * \
                np.arctan2(np.sqrt(np.abs((A - G) * np.cos(wpOme))),
                           np.sqrt(tg2iAG))
            # Calcul de a1
            a1 = np.sqrt((C*C + H*H) / np.sin(incl)**2)

            tanis2 = np.tan(incl/2.0)
            if tanis2 > 0:
                # Termes de calcul de l'incertitude
                G2mA2 = G*G - A*A
                cosmcosp = np.cos(wmOme)*np.cos(wpOme)
                tA = 2.*G*cosmcosp + G2mA2*(sinOcosO*tAw + sinwcosw*tAO)
                tB = G2mA2*(sinOcosO*tBw + sinwcosw*tBO)
                tF = G2mA2*(sinOcosO*tFw + sinwcosw*tFO)
                tG = -2.*A*cosmcosp + G2mA2*(sinOcosO*tGw + sinwcosw*tGO)

                sigincl = np.sqrt(tA*tA*covMat[0, 0] + tB*tB*covMat[1, 1] + tF*tF*covMat[2, 2] + tG*tG*covMat[3, 3]
                                  + 2.0 * (tA*tB*covMat[0, 1] + tA*tF*covMat[0, 2] + tA*tG*covMat[0, 3] +
                                           tB*tF*covMat[1, 2] + tB*tG*covMat[1, 3] + tF*tG*covMat[2, 3]))/(tanis2 * (1.0 + tanis2*tanis2) * tg2iAG*tg2iAG)
                # Calcul de sig_a1
                tCH = (C*C + H*H) * np.cos(incl) / (a1*np.sin(incl) **
                                                    3 * tanis2 * (1.0 + tanis2*tanis2) * tg2iAG*tg2iAG)
                tA = tA * tCH
                tB = tB * tCH
                tF = tF * tCH
                tG = tG * tCH
                tC = C / (a1 * np.sin(incl)**2)
                tH = H / (a1 * np.sin(incl)**2)

                siga1 = np.sqrt(tA*tA*covMat[0, 0] + tB*tB*covMat[1, 1] + tF*tF*covMat[2, 2] +
                                tG*tG*covMat[3, 3] + tC*tC *
                                covMat[4, 4] + tH*tH*covMat[5, 5]
                                + 2.0 * (tA*tB*covMat[0, 1] + tA*tF*covMat[0, 2] + tB*tF*covMat[1, 2] +
                                         tA*tG*covMat[0, 3] + tB*tG*covMat[1, 3] + tF*tG*covMat[2, 3] +
                                         tA*tC*covMat[0, 4] + tB*tC*covMat[1, 4] + tF*tC*covMat[2, 4] +
                                         tG*tC*covMat[3, 4] + tA*tH*covMat[0, 5] + tB*tH*covMat[1, 5] +
                                         tF*tH*covMat[2, 5] + tG*tH*covMat[3, 5] + tC*tH*covMat[4, 5]))

        # si tg2iBF est le plus grand denominateur
        else:
            # Calcul de i
            incl = 2.0 * \
                np.arctan2(np.sqrt(np.abs((B + F) * np.sin(wpOme))),
                           np.sqrt(tg2iBF))
            # Calcul de a1
            a1 = np.sqrt((C*C + H*H) / np.sin(incl)**2)
            # Calcul de sig_i :
            tanis2 = np.tan(incl/2.0)

            if tanis2 > 0:
                # Termes de calcul de l'incertitude
                F2mB2 = F*F - B*B
                sinmsinp = np.sin(wmOme)*np.sin(wpOme)
                tA = F2mB2*(-sinOcosO*tAw + sinwcosw*tAO)
                tB = 2.0*F*sinmsinp + F2mB2*(-sinOcosO*tBw + sinwcosw*tBO)
                tF = -2.0*B*sinmsinp + F2mB2*(-sinOcosO*tFw + sinwcosw*tFO)
                tG = F2mB2*(-sinOcosO*tGw + sinwcosw*tGO)

                sigincl = np.sqrt(tA*tA*covMat[0, 0] + tB*tB*covMat[1, 1] + tF*tF*covMat[2, 2] + tG*tG*covMat[3, 3]
                                  + 2.0 * (tA*tB*covMat[0, 1] + tA*tF*covMat[0, 2] + tA*tG*covMat[0, 3] +
                                           tB*tF*covMat[1, 2] + tB*tG*covMat[1, 3] + tF*tG*covMat[2, 3])) / (tanis2 * (1.0 + tanis2*tanis2) * tg2iBF*tg2iBF)

                # Calcul de sig_a1
                tCH = (C*C + H*H) * np.cos(incl) / (a1*np.sin(incl) **
                                                    3 * tanis2 * (1.0 + tanis2*tanis2) * tg2iBF*tg2iBF)
                tA = tA * tCH
                tB = tB * tCH
                tF = tF * tCH
                tG = tG * tCH
                tC = C / (a1 * np.sin(incl)**2)
                tH = H / (a1 * np.sin(incl)**2)

                siga1 = np.sqrt(tA*tA*covMat[0, 0] + tB*tB*covMat[1, 1] + tF*tF*covMat[2, 2] +
                                tG*tG*covMat[3, 3] + tC*tC *
                                covMat[4, 4] + tH*tH*covMat[5, 5]
                                + 2.0 * (tA*tB*covMat[0, 1] + tA*tF*covMat[0, 2] + tB*tF*covMat[1, 2] +
                                         tA*tG*covMat[0, 3] + tB*tG*covMat[1, 3] + tF*tG*covMat[2, 3] +
                                         tA*tC*covMat[0, 4] + tB*tC*covMat[1, 4] + tF*tC*covMat[2, 4] +
                                         tG*tC*covMat[3, 4] + tA*tH*covMat[0, 5] + tB*tH*covMat[1, 5] +
                                         tF*tH*covMat[2, 5] + tG*tH*covMat[3, 5] + tC*tH*covMat[4, 5]))

        #  Calcul du demi-grand axe
        u = (A*A + B*B + F*F + G*G) / 2.0
        v = A*G - B*F
        racu2v2 = np.sqrt((u + v)*(u - v))
        a0 = np.sqrt(u + racu2v2)

        tA = A + (u*A - v*G)/racu2v2
        tB = B + (u*B + v*F)/racu2v2
        tF = F + (u*F + v*B)/racu2v2
        tG = G + (u*G - v*A)/racu2v2

        siga0 = np.sqrt(tA*tA*covMat[0, 0] + tB*tB*covMat[1, 1] + tF*tF*covMat[2, 2] + tG*tG*covMat[3, 3]
                        + 2.0 * (tA*tB*covMat[0, 1] + tA*tF*covMat[0, 2] + tA*tG*covMat[0, 3] +
                                 tB*tF*covMat[1, 2] + tB*tG*covMat[1, 3] + tF*tG*covMat[2, 3])) / (2.0 * a0)

        return {"a0": a0,
                "inclination": incl*180/np.pi,
                "arg_periastron": w*180/np.pi,
                "nodeangle": Ome*180/np.pi,
                "a1": a1,
                "a0_error": siga0,
                "inclination_error": sigincl*180/np.pi,
                "arg_periastron_error": sigw*180/np.pi,
                "nodeangle_error": sigOme*180/np.pi,
                "a1_error": siga1}

    def campbell(self):
        star_type = self._star["nss_solution_type"]
        if not star_type.startswith("Orbital") and star_type != "AstroSpectroSB1":
            raise("Cannot compute Campbell parameters for star type {}".format(star_type))

        cols = ["a_thiele_innes", "b_thiele_innes", "f_thiele_innes",
                "g_thiele_innes", "c_thiele_innes", "h_thiele_innes"]
        
        covmat = self.covmat().reindex(index=cols, columns=cols, fill_value=0.0).to_numpy()
        result = self._TICH_errors(covmat,
                                   self._star["a_thiele_innes"],
                                   self._star["b_thiele_innes"],
                                   self._star["f_thiele_innes"],
                                   self._star["g_thiele_innes"],
                                   self._star["c_thiele_innes"],
                                   self._star["h_thiele_innes"])
        if np.isnan(self._star["g_thiele_innes_error"]):
            result["arg_periastron_error"] = np.nan
        result["source_id"] = self._star["source_id"]
        return pd.DataFrame([result])
