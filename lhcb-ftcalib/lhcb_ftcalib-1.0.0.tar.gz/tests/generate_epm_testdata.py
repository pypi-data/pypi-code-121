import os
import sys
import uproot
import lhcb_ftcalib as ft


def generate_reference_data(N):
    if not os.path.exists("tests/epm_reference_data"):
        os.mkdir("tests/epm_reference_data")

    with uproot.recreate("tests/epm_reference_data/reference.root") as File:
        poly1_MISTAG = ft.PolynomialCalibration(2, ft.link.mistag)
        poly2_MISTAG = ft.PolynomialCalibration(3, ft.link.mistag)
        poly1_LOGIT  = ft.PolynomialCalibration(2, ft.link.logit)

        params_poly1 = [[0, 0, 0, 0],
                        [0.01, 0.3, 0.01, 0],
                        [0.01, -0.05, 0.01, 0.1]]
        params_poly2 = [[0, 0, 0, 0, 0, 0],
                        [0.01, 0.3, -0.03, 0.01, 0, 0.04],
                        [0.01, -0.05, -0.3, 0.01, 0.1, 0.8]]

        generator = ft.toy_tagger.ToyDataGenerator()

        File["BU_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = False,
            DM           = 0,
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BS_POLY1_MISTAG"] = generator(
            N            = N,
            func         = poly1_MISTAG,
            params       = params_poly1,
            osc          = True,
            DM           = 17.761,  # EPM value
            DG           = 0.0913,  # EPM value
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY1_LOGIT"] = generator(
            N            = N,
            func         = poly1_LOGIT,
            params       = params_poly1,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])
        File["BD_POLY2_MISTAG"] = generator(
            N            = N,
            func         = poly2_MISTAG,
            params       = params_poly2,
            osc          = True,
            DM           = 0.51,  # EPM value
            DG           = 0,
            Aprod        = 0,
            lifetime     = 1.52,
            tagger_types = ["OSMuon", "OSKaon", "SSPion"],
            tag_effs     = [0.99, 0.9, 0.8])


if __name__ == "__main__":
    generate_reference_data(int(sys.argv[1]))
