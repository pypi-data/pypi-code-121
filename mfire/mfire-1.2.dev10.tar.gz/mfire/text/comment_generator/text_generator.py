"""
    [PROMETHEE] Module for text generation
"""

import numpy as np
import xarray as xr
from collections import defaultdict
from typing import Union, Sequence
import re

from mfire.utils.date import Period
from mfire.text.period_describer import PeriodDescriber
from mfire.settings import get_logger
from mfire.utils.formatter import get_synonym
from mfire.composite import AggregationType, LogicalOperator, RiskComponentComposite


# Logging
LOGGER = get_logger(name="comment.generator.mod", bind="comment_generator")

list_vent = [
    "FF__HAUTEUR10",
    "FF__HAUTEUR10__MAXE",
    "FF__HAUTEUR10__MINE",
    "FF__HAUTEUR10__Q10",
    "FF__HAUTEUR10__Q20",
    "FF__HAUTEUR10__Q30",
    "FF__HAUTEUR10__Q40",
    "ws" "FF__HAUTEUR10__Q50",
    "FF__HAUTEUR10__Q60",
    "FF__HAUTEUR10__Q70",
    "FF__HAUTEUR10__Q80",
    "FF__HAUTEUR10__Q90",
    "FF__HAUTEUR50",
    "FF__HAUTEUR100",
    "FF__HAUTEUR100",
    "FF__HAUTEUR100__MAXE",
    "FF__HAUTEUR100__MINE",
    "FF__HAUTEUR100__Q10",
    "FF__HAUTEUR100__Q20",
    "FF__HAUTEUR100__Q30",
    "FF__HAUTEUR100__Q40",
    "FF__HAUTEUR100__Q50",
    "FF__HAUTEUR100__Q60",
    "FF__HAUTEUR100__Q70",
    "FF__HAUTEUR100__Q80",
    "FF__HAUTEUR100__Q90",
    "si10",
]

list_rafales = [
    "RAF__HAUTEUR10",
    "RAF__HAUTEUR10__MAXE",
    "RAF__HAUTEUR10_MINE",
    "RAF__HAUTEUR10__Q10",
    "RAF__HAUTEUR10__Q20",
    "RAF__HAUTEUR10__Q30",
    "RAF__HAUTEUR10__Q40",
    "RAF__HAUTEUR10__Q50",
    "RAF__HAUTEUR10__Q60",
    "RAF__HAUTEUR10__Q70",
    "RAF__HAUTEUR10__Q80",
    "RAF__HAUTEUR10__Q90",
    "RAF__HAUTEUR50",
    "RAF__HAUTEUR100",
    "gust",
    "paramId_0",
]

list_neige = [
    "NEIPOT24__SOL",
    "NEIPOT1__SOL",
    "NEIPOT3__SOL",
    "NEIPOT6__SOL",
    "NEIPOT9__SOL",
    "NEIPOT12__SOL",
    "NEIGE__SOL",
    "NEIPOT__SOL",
    "NEIPOT__SOL",
    "NEIPOT__SOL",
    "NEIPOT__SOL__MAXE",
    "NEIPOT__SOL__MINE",
    "NEIPOT__SOL__Q10",
    "NEIPOT__SOL__Q20",
    "NEIPOT__SOL__Q30",
    "NEIPOT__SOL__Q40",
    "NEIPOT__SOL__Q50",
    "NEIPOT__SOL__Q60",
    "NEIPOT__SOL__Q70",
    "NEIPOT__SOL__Q80",
    "NEIPOT__SOL__Q90",
    "PROB_NEIGE__SOL",
]

list_precip = [
    "PRECIP__SOL",
    "PRECIP1__SOL",
    "PRECIP3__SOL",
    "PRECIP6__SOL",
    "PRECIP9__SOL",
    "PRECIP12__SOL",
    "PRECIP24__SOL",
    "EAU1__SOL",
    "EAU3__SOL",
    "EAU6__SOL",
    "EAU9__SOL",
    "EAU12__SOL",
    "EAU24__SOL",
    "PRECIP__SOL__MAXE",
    "PRECIP__SOL__MINE",
    "PRECIP__SOL__Q10",
    "PRECIP__SOL__Q20",
    "PRECIP__SOL__Q30",
    "PRECIP__SOL__Q40",
    "PRECIP__SOL__Q50",
    "PRECIP__SOL__Q60",
    "PRECIP__SOL__Q70",
    "PRECIP__SOL__Q80",
    "PRECIP__SOL__Q90",
    "PROB_PRECIP__SOL",
    "tp",
]

list_nebul = [
    "NEBUL__SOL",
    "NEBUL__SOL",
    "NEBUL__SOL",
    "NEBUL__SOL__P0",
    "NEBUL__SOL__P1",
    "NEBUL__SOL__P2",
    "NEBUL__SOL__P3",
    "NEBUL__SOL__P4",
    "NEBUL__SOL__P5",
    "NEBUL__SOL__P6",
    "NEBUL__SOL__P7",
    "NEBUL__SOL__P8",
    "NEBBAS__SOL",
    "NEBMOY__SOL",
    "NEBHAU__SOL",
]

list_visi = [
    "PROB_VISI__SOL",
    "VISI__SOL",
    "VISI__SOL__MAXE",
    "VISI__SOL__MINE",
    "VISI__SOL__Q10",
    "VISI__SOL__Q20",
    "VISI__SOL__Q30",
    "VISI__SOL__Q40",
    "VISI__SOL__Q50",
    "VISI__SOL__Q60",
    "VISI__SOL__Q70",
    "VISI__SOL__Q80",
    "VISI__SOL__Q90",
]

list_words = [
    "le",
    "la",
    "les",
    "ce",
    "cet",
    "cette",
    "demain",
    "aujourd'hui",
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

NO_VALUE = -9999


def get_riskname_evt(weatherVarName):
    # LOGGER.warning(f"Dans get_riskname_evt: {weatherVarName}")
    if weatherVarName in list_nebul:
        name = "nébulosité"
    elif weatherVarName in list_visi:
        name = "brouillard"
    else:
        name = ""
    return name


def get_prefix(variable):
    prefix = variable.split("_")[0]
    pattern = r"[0-9]"
    prefix = re.sub(pattern, "", prefix)
    return prefix


def get_accum(variable):
    """
    Permet d'avoir le nombre d'heure sur lequel la variable est cumulé.
    Args:
            variable (str): Le nom de la variable

    Returns:
        [str]: le nombre d'heure sur lequel la variable est cumulée
    """
    full_prefix = variable.split("_")[0]
    prefix = get_prefix(variable)
    accum = full_prefix.replace(prefix, "")
    if int(accum) > 1:
        accum_text = "sur " + str(accum) + " heures"
    else:
        if prefix == "NEIPOT":
            accum_text = "horaire"
        else:
            accum_text = "horaires"
    return accum, accum_text


class GenerationText:
    """Class for generating "Monozone" comments

        Args:
            component (RiskComponentComposite): component to describe
    """

    def __init__(self, component: RiskComponentComposite):
        self.component = component  # must be computed
        self.risks_ds = component.risks_ds
        self.final_risk_level = component.final_risk_da

        self.period_describer = PeriodDescriber(self.component.production_datetime)
        # On rajoute les identifiants de  la conf au module de log.
        global LOGGER
        LOGGER = LOGGER.bind(
            id=self.component.id,
            production_id=self.component.production_id,
            hazard=self.component.hazard,
            customer=self.component.customer,
            production_datetime=self.component.production_datetime,
        )

    def raise_exception(self):
        """
            On lève une exception si self.risks_ds et self.final_risk_level n'ont pas
            le même contenu pour les coordonnées valid_time
        """
        list_dims = ["valid_time"]
        for elt in list_dims:
            if (self.risks_ds[elt].values != self.final_risk_level[elt].values).all():
                raise ValueError(
                    f"Le contenu dans '{elt}' du dataset et du dataarray"
                    "donnés en entrée ne correspondent pas."
                )

    @staticmethod
    def upper_to_lower(comment):
        """
            Cette fonction permet de mettre en minuscule les lettres majuscules
            en milieu de phrase.
        """
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        liste_idx = []
        for (i, c) in enumerate(comment):
            if c == c.upper() and c.lower() in alphabet:
                liste_idx.append(i)
        for idx in liste_idx:
            if idx != 0:
                if comment[idx - 2] != ".":
                    comment = (
                        comment[:idx] + comment[idx].lower() + comment[(idx + 1) :]
                    )
        return comment

    def start_stop_echeances(self, da_period):
        """
            The rule is the following:
                - if there are more than 5 hours between two periods where
                    the risk is achieved, so we do not combine the periods
                - else: we combine the periods

            Argument:
                da_period {xarray.DataArray} -- dataarray of datetime64

            Returns:
                List of tuples (start,stop) to determine the different periods
                    where the risk is achieved.
        """
        if not isinstance(da_period, (np.ndarray, xr.core.dataarray.DataArray)):
            raise TypeError(
                f"type(da_period) = {type(da_period)}.\n"
                "L'argument en entrée <da_period> doit être une dataarray "
                "ou une numpy array."
            )

        elif not list(da_period):
            raise ValueError(
                f"len(da_period) = {len(da_period)}.\n"
                "L'argument en entrée <da_period> doit être non vide."
            )

        couples_start_stop = []
        start = da_period[0]
        if len(da_period) == 1:
            stop = da_period[0]
        else:
            for i in range(len(da_period) - 1):
                if (da_period[i + 1] != da_period[i] + np.timedelta64(1, "h")) and (
                    da_period[i + 1] > da_period[i] + np.timedelta64(5, "h")
                ):
                    stop = da_period[i]
                    couples_start_stop.append(Period(start, stop))
                    start = da_period[i + 1]
                stop = da_period[-1]
        couples_start_stop.append(Period(start, stop))
        return couples_start_stop

    @staticmethod
    def round_to_5(x):
        """
            Fonction pour arrondir des valeurs à l'entier divisible par
            5 le plus proche.
            (Fonction appliquée en particulier aux valeurs de rafales de vent)
            Exemples:
                Input --> Output
                 40   -->  40
                 42   -->  45
                 12   -->  15
                 25   -->  25
                15.3  -->  20
        """
        if x is None:
            return None

        if x % 5 > 0:
            x = (int(x / 5)) * 5 + 5
        else:
            x = (int(x / 5)) * 5
        return x

    @staticmethod
    def environ():
        return get_synonym("à environ") + " "

    @staticmethod
    def force_pluie(elt0, elt1):
        if int(elt0) > int(elt1):
            plus_ou_moins = "moins "
        else:
            plus_ou_moins = "plus "
        return plus_ou_moins + get_synonym("fort")

    def factorise_comment(
        self,
        idx,
        weatherVarName,
        rep_value_plain,
        rep_value_mountain,
        expression,
        risk_val,
        func,
    ):
        """
            Cette fonction permet de décrire, dans le commentaire final, les valeurs
            en montagne si elles existent et si elles vérifient certaines conditions.
        """
        comment = ""
        if (rep_value_mountain != NO_VALUE) and (rep_value_plain != NO_VALUE):
            threshold = self.component.get_threshold(risk_val, idx, "mountain")
            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                val = 5
            else:
                val = 0
            operator = next(
                lvl.elements_event[idx].mountain.comparison_op
                for lvl in self.component.levels
                if lvl.level == risk_val
            )
            condition = operator(func(rep_value_mountain), threshold - val)
            if (
                (func(rep_value_plain) != func(rep_value_mountain))
                and (abs(func(rep_value_plain) - func(rep_value_mountain)) != val)
                and condition
            ):
                comment += " en plaine, et " + expression + " en montagne"
        return comment

    @staticmethod
    def desc_comment(risk_name, comment):
        """
        """
        if (risk_name != "") and (risk_name is not None):
            if risk_name[0].lower() in "aeiouy":
                comment += "d'"
            else:
                comment += "de "
        else:
            comment += ""
        return comment

    @staticmethod
    def desc_period(text_period_debut):
        """
        """
        idx = text_period_debut.index(" ")
        if text_period_debut[0:idx].lower() in list_words:
            comment_period = "dès "
        else:
            comment_period = get_synonym("débutant") + " "
        comment_period += text_period_debut
        return comment_period

    def describe_periods(self, periods: Union[Period, Sequence[Period]]) -> str:
        """describe_periods: Gives a textual description of given periods

        Args:
            periods (Union[Period, Sequence[Period]]): Period or list of period
            to describe.

        Returns:
            str: Textual description
        """
        return self.period_describer.describe(periods)

    def get_period(self, risk_period):
        """
            Arguments:
                risk_period {xarray.DataArray} -- DataArray (ou numpy array)
                contenant des valid_time de type datetime64.

            Retourne:
                {String} -- une phrase qui décrit la période
        """
        periods_list = self.start_stop_echeances(risk_period)
        if len(periods_list) > 2:
            return "temporairement"
        else:
            return self.describe_periods(periods_list)

    @staticmethod
    def get_lists(risk_period_min, risk_period_max, elt_min, elt_max):
        """
            Factorisation de code
            --> Fonction utilisée dans la méthode compute_palier_different_levels()

            Cette fonction permet de créer une liste de deux éléments où le premier
            élément est une caractéristique correspondant au risque qui s'est déclenché
            avant le deuxième élément. Ceci nous permet de décrire les risques en
            respectant la temporalité.
        """
        list_elt = []
        comparison = risk_period_min[0] < risk_period_max.values[0]
        if comparison.all():
            list_elt.append(elt_min)
            list_elt.append(elt_max)
        else:
            list_elt.append(elt_max)
            list_elt.append(elt_min)

        return list_elt

    def get_repvalue(self, var, evt_val, id_area, risk_val):
        """
            Fonction qui retourne la valeur représentative maximale correspondant
            aux caractéristiques données en argument.

            Arguments:
                var {String} -- variable 'rep_value_plain' ou 'rep_value_mountain'
                    présente dans le dataset self.risks_ds
                id_area {String} -- id de la zone
                risk_val {int} -- valeur du niveau de risque

            Retourne:
                rep_value {xarray.DataArray} -- valeur représentative maximale
        """
        rep_value = NO_VALUE
        if var in self.risks_ds.data_vars:
            da_rep_value = (
                self.risks_ds[var]
                .isel(evt=evt_val)
                .sel(id=id_area)
                .sel(risk_level=risk_val)
                .round()
            )
            if not np.isnan(da_rep_value).all():
                rep_value = da_rep_value.max().values
        return rep_value

    def get_units(self, risk_level, evt):
        """ get_units : méthode qui recupere l'unité des valeurs contenues dans le
        self.risks_ds pour un evt et un risk_level donnés.
        Si self.risks_ds ne contient pas d'attribut 'units' (cas d'une variable
        sans unités) ou si l'argument risk_level ou evt n'existent pas, on renvoie
        une chaine de caractère vide ''.

        Args:
            risk_level (int) : niveau de risque
            evt (int) : index de l'evenement dans le dataset self.risks_ds

        Returns:
            str : unité
        """
        if "units" in self.risks_ds:
            try:
                return str(
                    self.risks_ds.units.sel(risk_level=risk_level).isel(evt=evt).values
                )
            except KeyError:
                LOGGER.error(
                    "Wrong key passed as 'evt' or 'risk_level'.",
                    risk_level=risk_level,
                    evt=evt,
                    exc_info=True,
                )
                return ""
        LOGGER.info("No attribute 'units' found in dataset")
        return ""

    @staticmethod
    def choice_rep_value(rep_value_plain, rep_value_mountain):
        """
        """
        if rep_value_plain == NO_VALUE:
            rep_value = rep_value_mountain
        else:
            rep_value = rep_value_plain
        return rep_value

    def get_text_period(self, var, dataarray, val):
        """
            Fonction qui retourne le texte décrivant la période.
        """
        text_period = ""
        if var in self.risks_ds.data_vars:
            risk_period = dataarray[dataarray == val].valid_time
            text_period = self.get_period(risk_period)
        return text_period

    def get_repvalue_textperiod(self, var, id_area, risk_val):
        """
            Fonction qui retourne la valeur representative et le texte décrivant
            la période.
        """
        rep_value = NO_VALUE
        text_period = ""
        if var in self.risks_ds.data_vars:
            dataarray = (
                self.risks_ds[var]
                .isel(evt=0)
                .sel(id=id_area)
                .sel(risk_level=risk_val)
                .round()
            )
            if not np.isnan(dataarray).all():
                rep_value = dataarray.max()
                risk_period = dataarray[dataarray == rep_value].valid_time
                text_period = self.get_period(risk_period)
        return rep_value, text_period

    def get_text_period_simple(self, dataarray, risk_val):
        """
            Fonction qui retourne le texte décrivant la période
            (lorsqu'une seule période existe, exemple pour le cas compute_pic).
        """
        risk_period = dataarray[dataarray == risk_val].valid_time
        return self.describe_periods(Period(risk_period.min(), risk_period.max()))

    @staticmethod
    def get_info_risk(dict_info_risk, val):
        """
            Pour un dictionnaire et une clé donnée, cette fonction renvoie
            les éléments correspondants.
        """
        keys_info = list(dict_info_risk.keys())
        for cle in keys_info:
            if cle == val:
                weatherVarName = dict_info_risk[cle][0]
                rep_value_plain = dict_info_risk[cle][1]
                rep_value_mountain = dict_info_risk[cle][2]
                unit = dict_info_risk[cle][3]
                idx_evt = dict_info_risk[cle][4]
        return weatherVarName, rep_value_plain, rep_value_mountain, unit, idx_evt

    def factorise_mod_gen(
        self, weatherVarName, idx, rep_value_plain, rep_value_mountain, unit, risk_max
    ):
        """
        """
        comment = ""
        rep_value = self.choice_rep_value(rep_value_plain, rep_value_mountain)

        if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
            if weatherVarName in list_vent:
                comment += "Vent maximal prévu "
            elif weatherVarName in list_rafales:
                comment += "Rafales maximales prévues "
            comment += self.environ() + str(self.round_to_5(rep_value)) + unit
            expression = (
                self.environ() + str(self.round_to_5(rep_value_mountain)) + unit
            )
            comment += self.factorise_comment(
                idx,
                weatherVarName,
                rep_value_plain,
                rep_value_mountain,
                expression,
                risk_max,
                self.round_to_5,
            )
        elif (weatherVarName in list_neige) or (weatherVarName in list_precip):
            accum, accum_texte = get_accum(weatherVarName)
            if weatherVarName in list_neige:
                comment += f"Potentiel de neige {accum_texte} maximal prévu à "
            elif weatherVarName in list_precip:
                comment += f"Cumuls {accum_texte} maximaux prévus de "
            comment += str(int(rep_value)) + unit
            expression = str(int(rep_value_mountain)) + unit
            comment += self.factorise_comment(
                idx,
                weatherVarName,
                rep_value_plain,
                rep_value_mountain,
                expression,
                risk_max,
                int,
            )
        else:
            comment = get_riskname_evt(weatherVarName)
        return comment

    def get_info_risk_aval(self, final_risk, risk_val, id_area):
        dict_info_risk = {}
        nb_evt = self.component.get_nb_evts([risk_val])[0]

        for i in range(nb_evt):
            weatherVarName = str(
                self.risks_ds.weatherVarName.sel(risk_level=risk_val).isel(evt=i).values
            )
            unit = self.get_units(risk_level=risk_val, evt=i)
            rep_value_plain = self.get_repvalue("rep_value_plain", i, id_area, risk_val)
            rep_value_mountain = self.get_repvalue(
                "rep_value_mountain", i, id_area, risk_val
            )
            if not ((rep_value_mountain == NO_VALUE) and (rep_value_plain == NO_VALUE)):
                dict_info_risk[weatherVarName] = [
                    rep_value_plain,
                    rep_value_mountain,
                    unit,
                    i,
                ]

        return dict_info_risk

    def mod_gen_cas_aval(self, final_risk, risk_val, id_area):
        """
            Module générique, traitement du cas aval OU/ET + cas amont ET
        """
        LOGGER.info("Generic cas aval", CommentKey="compute_aval")
        dict_info_risk = self.get_info_risk_aval(final_risk, risk_val, id_area)

        risk_period = final_risk[final_risk == risk_val].valid_time
        if (
            (len(self.start_stop_echeances(risk_period)) == 1)
            and (risk_period[0] == final_risk.valid_time[0])
            and (risk_period[-1] == final_risk.valid_time[-1])
        ):
            text_period = "sur toute la période"
        else:
            text_period = self.get_period(risk_period)

        if dict_info_risk != {}:
            keys = list(dict_info_risk.keys())
            comment = text_period.capitalize() + ", "
            for weatherVarName in keys:
                comment += (
                    self.factorise_mod_gen(
                        weatherVarName,
                        dict_info_risk[weatherVarName][3],
                        dict_info_risk[weatherVarName][0],
                        dict_info_risk[weatherVarName][1],
                        dict_info_risk[weatherVarName][2],
                        risk_val,
                    )
                    + ". "
                )
            comment = comment[:-1]
            return self.upper_to_lower(comment)
        else:
            comment = "Risque prévu " + text_period.capitalize() + "."
            return self.upper_to_lower(comment)

    def get_info_risk_amont(self, final_risk, risk_val, id_area):
        """
            Module générique, traitement du cas amont OU

            Dans ce cas-là, on doit dans un premier temps décrire
            (description temporelle + valeurs représentatives),
            tous les évènements qui ont allumé le
            risque, ensuite on décrit les autres évènements qui ne l'ont pas allumé,
            en donnant seulement leurs valeurs représentatives.

            Donc dans un premier temps, on crée deux dictionnaires:

            - un pour les évènements qui ont allumé le risque:
            >>> dict_info_risk_ok[weatherVarName] = [
            >>>    weatherVarName,
            >>>    rep_value_plain,
            >>>    rep_value_mountain,
            >>>    unit,
            >>>    i,
            >>> ]

            - et un pour les évènements qui n'ont pas allumé le risque:
            >>> dict_info_risk_nok[weatherVarName] = [
            >>>    rep_value_plain,
            >>>    rep_value_mountain,
            >>>    unit,
            >>>    i,
            >>> ]

            Puis on crée une liste de tuples (description_temporelle, weatherVarName).
            Cette liste associe chaque évènement (caractérisé par son weatherVarName)
            à sa description temporelle (début de matinée, fin de journée, ...).

            Et finalement on crée un dernier dictionnaire pour regrouper l'information
            des évènements qui ont allumé le risque au même moment:
            >>> dict_final[description_temporelle] = [
            >>>    weatherVarName_evt1,
            >>>     weatherVarName_evt2,
            >>>     weatherVarName_evt4,
            >>>     ...,
            >>> ]

            La fonction retourne ces trois dictionnaires.
        """

        dict_info_risk_ok = {}
        list_names = []
        list_text_period = []

        risk_period = final_risk[final_risk == risk_val].valid_time
        nb_evt = self.component.get_nb_evts([risk_val])[0]

        for i in range(nb_evt):
            weatherVarName = str(
                self.risks_ds.weatherVarName.sel(risk_level=risk_val).isel(evt=i).values
            )
            unit = self.get_units(risk_level=risk_val, evt=i)
            rep_value_plain = self.get_repvalue("rep_value_plain", i, id_area, risk_val)
            rep_value_mountain = self.get_repvalue(
                "rep_value_mountain", i, id_area, risk_val
            )
            occ_evt = (
                self.risks_ds.occurrence_event.sel(id=id_area)
                .sel(risk_level=risk_val)
                .isel(evt=i)
            )
            occ_evt_period = occ_evt[occ_evt == 1].valid_time
            final_period_evt = np.intersect1d(risk_period, occ_evt_period)

            if list(final_period_evt):
                text_period = self.get_period(final_period_evt)
                list_text_period.append(text_period)
                list_names.append(weatherVarName)
                dict_info_risk_ok[weatherVarName] = [
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    unit,
                    i,
                ]

        couples_period_name = [
            (elt1, elt2) for elt1, elt2 in zip(list_text_period, list_names)
        ]
        dict_final = defaultdict(list)
        for couple in couples_period_name:
            dict_final[couple[0]].append(couple[1])

        return dict(dict_final), dict_info_risk_ok

    def mod_gen_cas_amont_ou(self, final_risk, risk_max, id_area):
        """
            Module générique, traitement du cas amont OU
        """
        LOGGER.info("Module générique", CommentKey="generic_amont_ou")
        dict_text_name, dict_info_risk_ok = self.get_info_risk_amont(
            final_risk, risk_max, id_area
        )
        keys = list(dict_text_name.keys())
        values = list(dict_text_name.values())

        comment = ""
        for i in range(len(values)):
            comment += keys[i].capitalize()
            if len(values[i]) == 1:
                comment += ", "
                (
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    unit,
                    idx_evt,
                ) = self.get_info_risk(dict_info_risk_ok, values[i][0])
                comment += (
                    self.factorise_mod_gen(
                        weatherVarName,
                        idx_evt,
                        rep_value_plain,
                        rep_value_mountain,
                        unit,
                        risk_max,
                    )
                    + ". "
                )
            else:
                comment += " : "
                for j in range(len(values[i])):
                    (
                        weatherVarName,
                        rep_value_plain,
                        rep_value_mountain,
                        unit,
                        idx_evt,
                    ) = self.get_info_risk(dict_info_risk_ok, values[i][j])
                    comment += (
                        self.factorise_mod_gen(
                            weatherVarName,
                            idx_evt,
                            rep_value_plain,
                            rep_value_mountain,
                            unit,
                            risk_max,
                        )
                        + ", "
                    )
                comment = comment[:-2] + ". "

        comment = comment[:-1]
        comment = self.upper_to_lower(comment)

        return comment

    def module_generique(self, final_risk, risk_val, id_area):
        """
            Module générique global
        """
        level = next(lvl for lvl in self.component.levels if lvl.level == risk_val)
        if (
            level.aggregation_type == AggregationType.UP_STREAM
            and level.logical_op_list[0] == LogicalOperator.OR
        ):
            LOGGER.info("On passe dans le module générique, cas amont OU.")
            comment = self.mod_gen_cas_amont_ou(final_risk, risk_val, id_area)
        else:
            LOGGER.info(
                "On passe dans le module générique, cas amont ET ou cas aval ET/OU."
            )
            comment = self.mod_gen_cas_aval(final_risk, risk_val, id_area)
        return comment

    @staticmethod
    def compute_ras():
        """
            Case where the risk is not achieved.

            Returns only:
                "RAS" {str}
        """
        LOGGER.debug("Le type de commentaire est compute_ras.")
        return "R.A.S."

    def compute_global_idem(self, id_area):
        """
            Situation traitée ici:

            [
                3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3.,
                3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3.
            ]
            --> même niveau de risque partout

        """
        LOGGER.info(
            "Le type de commentaire est compute_global_idem",
            CommentKey="compute_global_idem",
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = self.component.get_final_risk_max_level(my_id=id_area)

        if self.component.get_nb_evts([risk_max])[0] == 1:

            rep_value_plain, text_period_plain = self.get_repvalue_textperiod(
                "rep_value_plain", id_area, risk_max
            )
            rep_value_mountain, text_period_mountain = self.get_repvalue_textperiod(
                "rep_value_mountain", id_area, risk_max
            )
            rep_value = self.choice_rep_value(rep_value_plain, rep_value_mountain)

            unit = self.get_units(risk_level=risk_max, evt=0)

            weatherVarName = str(
                self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
            )

            nb_risk = (final_risk == risk_max).sum()
            nb_ech = final_risk.count()

            if nb_risk.values / nb_ech.values > 0.9:
                comment = "Risque prévu sur toute la période"
            else:
                comment = "Risque prévu "
                comment += self.get_text_period_simple(final_risk, risk_max)

            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                if weatherVarName in list_vent:
                    comment += ". Vent maximal prévu : "
                elif weatherVarName in list_rafales:
                    comment += ". Rafales maximales prévues : "
                comment += (
                    self.environ()
                    + str(self.round_to_5(rep_value))
                    + unit
                    + " "
                    + text_period_plain
                )
                expression = (
                    self.environ()
                    + str(self.round_to_5(rep_value_mountain))
                    + unit
                    + " "
                    + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    self.round_to_5,
                )
            elif weatherVarName in list_neige:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f". Potentiel de neige {accum_texte} maximal prévu : "
                    + str(int(rep_value))
                    + unit
                    + " "
                    + text_period_plain
                )
                expression = (
                    str(int(rep_value_mountain)) + unit + " " + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            elif weatherVarName in list_precip:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f". Cumuls {accum_texte} maximaux prévus de "
                    + str(int(rep_value))
                    + unit
                    + " "
                    + text_period_plain
                )
                expression = (
                    "de "
                    + str(int(rep_value_mountain))
                    + unit
                    + " "
                    + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            comment += "."
        else:
            comment = self.module_generique(final_risk, risk_max, id_area)

        return comment

    def compute_global(self, id_area):
        """
            Pour les cas traités ici --> risk_min != 0

            [
                3., 3., 3., 4., 4., 3., 3., 4., 3., 3., 3., 3.,
                3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3., 3.
            ]
            Ou aussi:
            [
                2., 3., 2., 2., 3., 1., 1., 1., 1., 1., 2., 2.,
                3., 2., 2., 2., 3., 1., 1., 1., 1., 1., 1., 1.
            ]

        """
        LOGGER.info(
            "Le type de commentaire est compute_global", CommentKey="compute_global"
        )
        self.raise_exception()
        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)
        risk_min = min(final_risk.values)
        risk_levels = list(set(final_risk.values))

        if (self.component.get_nb_evts(risk_levels)[0] == 1) and (
            len(self.component.get_nb_evts(risk_levels)) == 1
        ):
            rep_value_plain, text_period_plain = self.get_repvalue_textperiod(
                "rep_value_plain", id_area, risk_max
            )
            rep_value_mountain, text_period_mountain = self.get_repvalue_textperiod(
                "rep_value_mountain", id_area, risk_max
            )
            rep_value = self.choice_rep_value(rep_value_plain, rep_value_mountain)
            if rep_value == rep_value_plain:
                var = "plain"
            else:
                var = "mountain"

            unit = self.get_units(risk_level=risk_max, evt=0)

            weatherVarName = str(
                self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
            )

            comment = "Risque prévu sur toute la période"

            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                if weatherVarName in list_vent:
                    comment += ". Vent supérieur à "
                elif weatherVarName in list_rafales:
                    comment += ". Rafales supérieures à "
                comment += (
                    str(int(self.component.get_threshold(risk_min, 0, var)))
                    + unit
                    + " avec un maximum atteint "
                    + text_period_plain
                    + " jusqu'à "
                    + str(self.round_to_5(rep_value))
                    + unit
                )
                expression = (
                    "jusqu'à "
                    + str(self.round_to_5(rep_value_mountain))
                    + unit
                    + " atteint "
                    + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    self.round_to_5,
                )
            elif weatherVarName in list_neige:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f". Potentiel de neige {accum_texte} supérieur à "
                    + str(int(self.component.get_threshold(risk_min, 0, var)))
                    + unit
                    + " avec un maximum atteint "
                    + text_period_plain
                    + " jusqu'à "
                    + str(int(rep_value))
                    + unit
                )
                expression = (
                    "jusqu'à "
                    + str(int(rep_value_mountain))
                    + unit
                    + " atteint "
                    + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            elif weatherVarName in list_precip:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f". Cumuls {accum_texte} maximaux prévus de "
                    + str(int(rep_value))
                    + unit
                    + " "
                    + text_period_plain
                )
                expression = (
                    str(int(rep_value_mountain)) + unit + " " + text_period_mountain
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            comment += "."
        else:
            comment = self.module_generique(final_risk, risk_max, id_area)

        return comment

    def compute_pic(self, id_area):
        """
            Situation traitée ici:
            [
                0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
                0., 0., 0., 0., 3., 0., 0., 0., 0., 0., 0., 0.
            ]

        """
        LOGGER.info("Le type de commentaire est compute_pic", CommentKey="compute_pic")
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)

        text_period = self.get_text_period_simple(final_risk, risk_max)

        if self.component.get_nb_evts([risk_max])[0] == 1:
            rep_value_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_max)
            rep_value_mountain = self.get_repvalue(
                "rep_value_mountain", 0, id_area, risk_max
            )
            rep_value = self.choice_rep_value(rep_value_plain, rep_value_mountain)

            unit = self.get_units(risk_level=risk_max, evt=0)

            weatherVarName = str(
                self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
            )

            comment = text_period.capitalize()

            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                if weatherVarName in list_vent:
                    comment += ", vent prévu "
                elif weatherVarName in list_rafales:
                    comment += ", rafales prévues "
                comment += self.environ() + str(self.round_to_5(rep_value)) + unit
                expression = (
                    self.environ() + str(self.round_to_5(rep_value_mountain)) + unit
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    self.round_to_5,
                )
            elif weatherVarName in list_neige:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f", potentiel de neige {accum_texte} prévu à "
                    + str(int(rep_value))
                    + unit
                )
                expression = str(int(rep_value_mountain)) + unit
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            elif weatherVarName in list_precip:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f", cumuls {accum_texte} prévus de " + str(int(rep_value)) + unit
                )
                expression = str(int(rep_value_mountain)) + unit
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_plain,
                    rep_value_mountain,
                    expression,
                    risk_max,
                    int,
                )
            else:
                comment = "Risque prévu " + text_period
            comment += "."
        else:
            comment = self.module_generique(final_risk, risk_max, id_area)

        return comment

    def compute_decroissance(self, id_area):
        """
            Situation traitée:
            [
                3., 3., 3., 3., 3., 3., 3., 3., 2., 2., 2., 2.,
                2., 2., 2., 2., 1., 1., 1., 1., 1., 1., 1., 1.
            ]

            Pas de cas générique ici.

        """
        LOGGER.info(
            "Le type de commentaire est compute_decroissance",
            CommentKey="compute_decroissance",
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)
        risk_min = min(final_risk.values)

        rep_value_max_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_max)
        rep_value_max_mountain = self.get_repvalue(
            "rep_value_mountain", 0, id_area, risk_max
        )
        rep_value_max = self.choice_rep_value(
            rep_value_max_plain, rep_value_max_mountain
        )

        rep_value_min_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_min)
        rep_value_min_mountain = self.get_repvalue(
            "rep_value_mountain", 0, id_area, risk_min
        )
        rep_value_min = self.choice_rep_value(
            rep_value_min_plain, rep_value_min_mountain
        )

        text_period_max = self.get_text_period_simple(final_risk, risk_max)

        unit_min = self.get_units(risk_level=risk_min, evt=0)
        unit_max = self.get_units(risk_level=risk_max, evt=0)

        weatherVarName = str(
            self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
        )

        comment = text_period_max.capitalize()

        risk_period_min = final_risk[final_risk == risk_min].valid_time
        text_period_debut = self.describe_periods(Period(risk_period_min.min()))
        text_period_min = self.desc_period(text_period_debut)

        if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
            if weatherVarName in list_vent:
                comment += ", vent "
            elif weatherVarName in list_rafales:
                comment += ", rafales "
            comment += self.environ() + str(self.round_to_5(rep_value_max)) + unit_max
            expression0 = (
                self.environ() + str(self.round_to_5(rep_value_max_mountain)) + unit_max
            )
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_max_plain,
                rep_value_max_mountain,
                expression0,
                risk_max,
                self.round_to_5,
            )
            comment += (
                ". Puis, atténuation progressive, "
                + text_period_min
                + ", jusqu'à environ "
                + str(self.round_to_5(rep_value_min))
                + unit_min
            )
            expression1 = (
                self.environ() + str(self.round_to_5(rep_value_min_mountain)) + unit_min
            )
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_min_plain,
                rep_value_min_mountain,
                expression1,
                risk_min,
                self.round_to_5,
            )
        elif weatherVarName in list_neige:
            accum, accum_texte = get_accum(weatherVarName)
            comment += (
                f", potentiel de neige {accum_texte} à "
                + str(int(rep_value_max))
                + unit_max
            )
            expression0 = str(int(rep_value_max_mountain)) + unit_max
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_max_plain,
                rep_value_max_mountain,
                expression0,
                risk_max,
                int,
            )
            comment += (
                " Puis, atténuation progressive, "
                + text_period_min
                + ", jusqu'à "
                + str(int(rep_value_min))
                + unit_min
            )
            expression1 = str(int(rep_value_min_mountain)) + unit_min
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_min_plain,
                rep_value_min_mountain,
                expression1,
                risk_min,
                int,
            )
        elif weatherVarName in list_precip:
            accum, accum_texte = get_accum(weatherVarName)
            comment += (
                f", cumuls {accum_texte} maximaux prévus de "
                + str(int(rep_value_max))
                + unit_max
            )
            expression = str(int(rep_value_max_mountain)) + unit_max
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_max_plain,
                rep_value_max_mountain,
                expression,
                risk_max,
                int,
            )
            comment += ". Puis atténuation des précipitations."
        else:
            comment = (
                "Risque prévu "
                + text_period_max
                + ", puis atténuation progressive "
                + text_period_min
            )
        comment += "."

        return comment

    def compute_decroissance_pluie(self, id_area):
        """
            Cette fonction concerne seulement les cumuls de pluie et traite
            le cas de décroissance progressive avec risk_min=0:
            (En effet, dans le cas de la pluie il est d'important de signaler
            la fin des précipitations (le passage du niveau 1 au niveau 0))

            [
                3., 3., 3., 2., 2., 1., 1., 1., 0., 0., 0., 0.,
                0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
            ]

            Pas de cas générique ici.

        """
        LOGGER.info(
            "Le type de commentaire est compute_decroissance_pluie",
            CommentKey="compute_decroissance_pluie",
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)
        risk_min = min(final_risk.values)

        rep_value_max_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_max)
        rep_value_max_mountain = self.get_repvalue(
            "rep_value_mountain", 0, id_area, risk_max
        )
        rep_value_max = self.choice_rep_value(
            rep_value_max_plain, rep_value_max_mountain
        )

        risk_period_min = final_risk[final_risk == risk_min].valid_time
        text_period_min = self.describe_periods(Period(risk_period_min.min()))

        text_period_max = self.get_text_period_simple(final_risk, risk_max)

        weatherVarName = str(
            self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
        )
        accum, accum_texte = get_accum(weatherVarName)
        unit = self.get_units(risk_level=risk_max, evt=0)

        comment = (
            text_period_max.capitalize()
            + f", cumuls {accum_texte} maximaux prévus de "
            + str(int(rep_value_max))
            + unit
        )
        expression = str(int(rep_value_max_mountain)) + unit
        comment += self.factorise_comment(
            0,
            weatherVarName,
            rep_value_max_plain,
            rep_value_max_mountain,
            expression,
            risk_max,
            int,
        )
        comment += ". Fin des pluies fortes " + text_period_min + "."

        return comment

    def compute_croissance(self, id_area):
        """
            Situation traitée:
            [
                1., 1., 1., 1., 1., 1., 1., 1., 2., 2., 2., 2.,
                2., 2., 2., 2., 3., 3., 3., 3., 3., 3., 3., 3.
            ]

            Pas de cas générique ici.

        """
        LOGGER.info(
            "Le type de commentaire est compute_croissance",
            CommentKey="compute_croissance",
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)
        risk_min = min(final_risk.values)

        text_period_min = self.get_text_period_simple(final_risk, risk_min)

        rep_value_max_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_max)
        rep_value_max_mountain = self.get_repvalue(
            "rep_value_mountain", 0, id_area, risk_max
        )
        rep_value_max = self.choice_rep_value(
            rep_value_max_plain, rep_value_max_mountain
        )

        rep_value_min_plain = self.get_repvalue("rep_value_plain", 0, id_area, risk_min)
        rep_value_min_mountain = self.get_repvalue(
            "rep_value_mountain", 0, id_area, risk_min
        )
        rep_value_min = self.choice_rep_value(
            rep_value_min_plain, rep_value_min_mountain
        )

        unit_min = self.get_units(risk_level=risk_min, evt=0)
        unit_max = self.get_units(risk_level=risk_max, evt=0)

        weatherVarName = str(
            self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
        )

        comment = text_period_min.capitalize()

        risk_period_max = final_risk[final_risk == risk_max].valid_time
        text_period_debut = self.describe_periods(Period(risk_period_max.min()))
        text_period_max = self.desc_period(text_period_debut)

        if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
            if weatherVarName in list_vent:
                comment += ", vent "
            elif weatherVarName in list_rafales:
                comment += ", rafales "
            comment += self.environ() + str(self.round_to_5(rep_value_min)) + unit_min
            expression0 = (
                self.environ() + str(self.round_to_5(rep_value_min_mountain)) + unit_min
            )
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_min_plain,
                rep_value_min_mountain,
                expression0,
                risk_min,
                self.round_to_5,
            )
            comment += (
                ". Puis, intensification progressive, "
                + text_period_max
                + ", jusqu'à atteindre environ "
                + str(self.round_to_5(rep_value_max))
                + unit_max
            )
            expression1 = (
                self.environ() + str(self.round_to_5(rep_value_max_mountain)) + unit_max
            )
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_max_plain,
                rep_value_max_mountain,
                expression1,
                risk_max,
                self.round_to_5,
            )
        elif weatherVarName in list_neige:
            accum, accum_texte = get_accum(weatherVarName)
            comment += (
                f", potentiel de neige {accum_texte} à "
                + str(int(rep_value_min))
                + unit_min
            )
            expression0 = str(int(rep_value_min_mountain)) + unit_min
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_min_plain,
                rep_value_min_mountain,
                expression0,
                risk_min,
                int,
            )
            comment += (
                ". Puis, intensification progressive, "
                + text_period_max
                + ", jusqu'à atteindre "
                + str(int(rep_value_max))
                + unit_max
            )
            expression1 = str(int(rep_value_max_mountain)) + unit_max
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_max_plain,
                rep_value_max_mountain,
                expression1,
                risk_max,
                int,
            )
        elif weatherVarName in list_precip:
            accum, accum_texte = get_accum(weatherVarName)
            comment += (
                f", cumuls {accum_texte} de " + str(int(rep_value_min)) + unit_min
            )
            expression = str(int(rep_value_min_mountain)) + unit_min
            comment += self.factorise_comment(
                0,
                weatherVarName,
                rep_value_min_plain,
                rep_value_min_mountain,
                expression,
                risk_min,
                int,
            )
            comment += ". Puis intensification des précipitations."
        else:
            comment += (
                "Risque prévu "
                + text_period_min
                + ", puis intensification progressive "
                + text_period_max
            )
        comment += "."

        return comment

    def compute_palier_different_levels(self, id_area):
        """
            On décrit la situation en respectant la temporalité.

             Deux types de situation:
            [
                0., 0., 0., 3., 3., 0., 0., 0., 0., 0., 0., 0.,
                0., 2., 2., 0., 0., 0., 0., 0., 0., 0., 0., 0.
            ]
            ([
                0., 0., 0., 2., 2., 0., 0., 0., 0., 0., 0., 0.,
                0., 3., 3., 0., 0., 0., 0., 0., 0., 0., 0., 0.
            ])


        To Do :
           A reprendre complètement.
           La on met vraiment des rustines dans des coins pour ne pas que ça explose ...
        """
        LOGGER.info(
            "Le type de commentaire est compute_palier_different_levels",
            CommentKey="compute_palier_different_levels",
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        set_val = set(final_risk.values)
        set_val.remove(0)

        risk_max = max(set_val)
        risk_min = min(set_val)

        dimension_variable = self.component.time_dimension

        risk_period_max = self.component.get_final_max_risk_period(
            my_id=id_area, coord="valid_time"
        )  # final_risk[final_risk == risk_max].valid_time
        risk_step_max = self.component.get_final_max_risk_period(
            my_id=id_area
        )  # final_risk[final_risk == risk_max].step
        text_period_rep_value_max = self.get_period(risk_period_max)

        risk_period_other = self.component.get_period_for_risk(
            my_id=id_area, coord="valid_time"
        )  # final_risk[final_risk != 0].valid_time
        risk_step_other = self.component.get_period_for_risk(
            my_id=id_area
        )  # final_risk[final_risk != 0].step

        risk_period_min = np.setdiff1d(risk_period_other.values, risk_period_max.values)
        risk_step_min = np.setdiff1d(risk_step_other.values, risk_step_max.values)
        text_period_rep_value_min = self.get_period(risk_period_min)

        list_text_period = self.get_lists(
            risk_period_min,
            risk_period_max,
            text_period_rep_value_min,
            text_period_rep_value_max,
        )
        list_risk = self.get_lists(risk_period_min, risk_period_max, risk_min, risk_max)

        # On va aller regarder les conditions sur les risques min et maximaux.
        compute_pallier = False
        if (len(self.component.get_nb_evts([risk_max, risk_min])) == 1) and (
            self.component.get_nb_evts([risk_max, risk_min])[0] == 1
        ):
            risk_max_info = self.component.select_risk_level(level=risk_max)
            dict_max = risk_max_info[0].get_singleEvt_comparison()
            risk_min_info = self.component.select_risk_level(level=risk_min)
            dict_min = risk_min_info[0].get_singleEvt_comparison()

            max_is_quantitative = dict_max.get("category") in [
                "quantitative",
                "restrictedQuantitative",
            ]
            min_is_quantitative = dict_min.get("category") in [
                "quantitative",
                "restrictedQuantitative",
            ]
            both_quantitative = min_is_quantitative and max_is_quantitative
            # On va plotter le dict_min et le dict_max
            if both_quantitative:
                compute_pallier = True

        if compute_pallier:
            # Ici il faut impérativement passer par la compréhension de la
            # conf pour savoir ce qui est disponible.
            if "rep_value_plain" in self.risks_ds.data_vars:
                da_rep_value_min_plain = (
                    self.risks_ds.rep_value_plain.isel(evt=0)
                    .sel(id=id_area)
                    .sel(risk_level=risk_min)
                    .round()
                )
                if not np.isnan(da_rep_value_min_plain).all():
                    list_rep_value_min_plain = []
                    for step in risk_step_min:
                        list_rep_value_min_plain.append(
                            da_rep_value_min_plain.sel({dimension_variable: step})
                        )
                    rep_value_min_plain = min(list_rep_value_min_plain)
                else:
                    LOGGER.info("On fix le min sur la plaine a NO_VALUE")
                    rep_value_min_plain = NO_VALUE

                rep_value_max_plain = self.get_repvalue(
                    "rep_value_plain", 0, id_area, risk_max
                )
                list_rep_values_plain = self.get_lists(
                    risk_period_min,
                    risk_period_max,
                    rep_value_min_plain,
                    rep_value_max_plain,
                )
            else:
                list_rep_values_plain = [NO_VALUE, NO_VALUE]

            if "rep_value_mountain" in self.risks_ds.data_vars:
                da_rep_value_min_mountain = (
                    self.risks_ds.rep_value_mountain.isel(evt=0)
                    .sel(id=id_area)
                    .sel(risk_level=risk_min)
                    .round()
                )
                if not np.isnan(da_rep_value_min_mountain).all():
                    list_rep_value_min_mountain = []
                    for step in risk_step_min:
                        list_rep_value_min_mountain.append(
                            da_rep_value_min_mountain.sel({dimension_variable: step})
                        )

                    rep_value_min_mountain = min(list_rep_value_min_mountain)
                else:
                    LOGGER.info("On fix le min a NO_VALUE")
                    rep_value_min_mountain = NO_VALUE
                rep_value_max_mountain = self.get_repvalue(
                    "rep_value_mountain", 0, id_area, risk_max
                )
                list_rep_values_mountain = self.get_lists(
                    risk_period_min,
                    risk_period_max,
                    rep_value_min_mountain,
                    rep_value_max_mountain,
                )
            else:
                list_rep_values_mountain = [NO_VALUE, NO_VALUE]

            unit0 = self.get_units(risk_level=list_risk[0], evt=0)
            unit1 = self.get_units(risk_level=list_risk[1], evt=0)

            weatherVarName = str(
                self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
            )

            comment = list_text_period[0].capitalize()

            rep_value_0 = self.choice_rep_value(
                list_rep_values_plain[0], list_rep_values_mountain[0]
            )
            rep_value_1 = self.choice_rep_value(
                list_rep_values_plain[1], list_rep_values_mountain[1]
            )

            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                if weatherVarName in list_vent:
                    mot = ", vent "
                elif weatherVarName in list_rafales:
                    mot = ", rafales "
                comment += (
                    mot + self.environ() + str(self.round_to_5(rep_value_0)) + unit0
                )
                expression0 = (
                    self.environ()
                    + str(self.round_to_5(list_rep_values_mountain[0]))
                    + unit0
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[0],
                    list_rep_values_mountain[0],
                    expression0,
                    list_risk[0],
                    self.round_to_5,
                )
                comment += (
                    ". Nouvel épisode {}, ".format(
                        self.force_pluie(rep_value_0, rep_value_1)
                    )
                    + list_text_period[1]
                    + mot
                    + self.environ()
                    + str(self.round_to_5(rep_value_1))
                    + unit1
                )
                expression1 = (
                    self.environ()
                    + str(self.round_to_5(list_rep_values_mountain[1]))
                    + unit1
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[1],
                    list_rep_values_mountain[1],
                    expression1,
                    list_risk[1],
                    self.round_to_5,
                )
            elif weatherVarName in list_neige:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f", potentiel de neige {accum_texte} à "
                    + str(int(rep_value_0))
                    + unit0
                )
                expression0 = "à " + str(int(list_rep_values_mountain[0])) + unit0
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[0],
                    list_rep_values_mountain[0],
                    expression0,
                    list_risk[0],
                    int,
                )
                comment += (
                    ". Nouvel épisode {}, ".format(
                        self.force_pluie(rep_value_0, rep_value_1)
                    )
                    + list_text_period[1]
                    + ", potentiel de neige à "
                    + str(int(rep_value_1))
                    + unit1
                )
                expression1 = "à " + str(int(list_rep_values_mountain[1])) + unit1
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[1],
                    list_rep_values_mountain[1],
                    expression1,
                    list_risk[1],
                    int,
                )
            elif weatherVarName in list_precip:
                accum, accum_texte = get_accum(weatherVarName)
                comment += f", cumuls {accum_texte} de " + str(int(rep_value_0)) + unit0
                expression0 = "de " + str(int(list_rep_values_mountain[0])) + unit0
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[0],
                    list_rep_values_mountain[0],
                    expression0,
                    list_risk[0],
                    int,
                )
                comment += (
                    ". Puis, deuxième épisode "
                    + list_text_period[1]
                    + " mais {}, cumuls de {}{}".format(
                        self.force_pluie(rep_value_0, rep_value_1),
                        str(int(rep_value_1)),
                        unit1,
                    )
                )
                expression1 = " de " + str(int(list_rep_values_mountain[1])) + unit1
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    list_rep_values_plain[1],
                    list_rep_values_mountain[1],
                    expression1,
                    list_risk[1],
                    int,
                )
            else:
                comment += (
                    "Risque prévu "
                    + list_text_period[0]
                    + ". Puis un second épisode "
                    + list_text_period[1]
                )
            comment += "."
        else:
            comment = self.module_generique(final_risk, risk_max, id_area)

        return comment

    def compute_others(self, id_area):
        """
            Quand aucune situation n'entre dans les fonctions précédentes,
            alors la situation est traitée ici et on prend en compte que le max.

        """
        LOGGER.info(
            "Le type de commentaire est compute_others", CommentKey="compute_other"
        )
        self.raise_exception()

        final_risk = self.final_risk_level.sel(id=id_area)
        risk_max = max(final_risk.values)

        risk_period = self.component.get_final_max_risk_period(
            my_id=id_area, coord="valid_time"
        )
        text_period = self.get_period(risk_period)
        text_period_debut = self.describe_periods(Period(risk_period.min()))
        text_period_fin = self.describe_periods(Period(risk_period.max()))

        if (len(self.start_stop_echeances(risk_period)) == 1) and (
            final_risk.valid_time.values[-1] == risk_period.values[-1]
        ):
            comment_period = self.desc_period(text_period_debut)
        elif (len(self.start_stop_echeances(risk_period)) == 2) and (
            final_risk.valid_time.values[-1] == risk_period.values[-1]
        ):
            comment_period = (
                text_period_debut
                + "{} à nouveau ".format(get_synonym(" puis"))
                + text_period_fin
            )
        else:
            comment_period = text_period

        if self.component.get_nb_evts([risk_max])[0] == 1:
            rep_value_max_plain = self.get_repvalue(
                "rep_value_plain", 0, id_area, risk_max
            )
            rep_value_max_mountain = self.get_repvalue(
                "rep_value_mountain", 0, id_area, risk_max
            )
            rep_value = self.choice_rep_value(
                rep_value_max_plain, rep_value_max_mountain
            )
            unit = self.get_units(risk_level=risk_max, evt=0)

            weatherVarName = str(
                self.risks_ds.isel(evt=0).weatherVarName.sel(risk_level=risk_max).values
            )

            comment = "Risque maximal prévu " + comment_period

            if (weatherVarName in list_vent) or (weatherVarName in list_rafales):
                if weatherVarName in list_vent:
                    comment += ", vent maximal prévu "
                elif weatherVarName in list_rafales:
                    comment += ", rafales maximales prévues "
                comment += self.environ() + str(self.round_to_5(rep_value)) + unit
                expression = (
                    self.environ() + str(self.round_to_5(rep_value_max_mountain)) + unit
                )
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_max_plain,
                    rep_value_max_mountain,
                    expression,
                    risk_max,
                    self.round_to_5,
                )
            elif weatherVarName in list_neige:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f", potentiel de neige {accum_texte} maximal prévu à "
                    + str(int(rep_value))
                    + unit
                )
                expression = str(int(rep_value_max_mountain)) + unit
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_max_plain,
                    rep_value_max_mountain,
                    expression,
                    risk_max,
                    int,
                )
            elif weatherVarName in list_precip:
                accum, accum_texte = get_accum(weatherVarName)
                comment += (
                    f", cumuls {accum_texte} maximaux prévus de "
                    + str(int(rep_value))
                    + unit
                )
                expression = "de " + str(int(rep_value_max_mountain)) + unit
                comment += self.factorise_comment(
                    0,
                    weatherVarName,
                    rep_value_max_plain,
                    rep_value_max_mountain,
                    expression,
                    risk_max,
                    int,
                )
            comment += "."
        else:
            comment = self.module_generique(final_risk, risk_max, id_area)

        return comment

    def identification_cas(self, id_area, print_details=False):
        """
            Fonction permettant d'identifier la situation dans laquelle le risque
            se trouve et ainsi exécuter la bonne méthode compute_() pour générer
            le commentaire adapté.
        """

        da = self.final_risk_level.sel(id=id_area)
        risk_max = max(da.values)
        risk_min = min(da.values)
        if risk_max != 0:
            risk_period_max = da[da == risk_max].valid_time
            risk_period_diff0 = da[da != 0].valid_time
            risk_period_other = np.setdiff1d(
                risk_period_diff0.values, risk_period_max.values
            )
            LOGGER.debug(f"Risk maximum {risk_max}")
            LOGGER.debug(self.risks_ds.weatherVarName.isel(evt=0))
            weatherVarName = str(
                self.risks_ds.weatherVarName.isel(evt=0).sel(risk_level=risk_max).values
            )

            if print_details:
                print(
                    "**************************************"
                    "**************************************"
                )
                print("Heures:")
                print(
                    "[00 1  2  3  4  5  6  7  8  9  10 11 12 13"
                    "14 15 16 17 18 19 20 21 22 23 \n 00]"
                )
                print(
                    "-------------------------------------"
                    "---------------------------------------"
                )
                print("Niveaux de risque:")
                print(da.values)
                print(
                    "--------------------------------------"
                    "--------------------------------------"
                )

            da_sorted_desc = da.sortby(da, ascending=False)
            da_sorted_asc = da.sortby(da, ascending=True)
            comparison_desc = da.values == da_sorted_desc.values
            comparison_asc = da.values == da_sorted_asc.values
            da_val = da.values

        if risk_max == 0:
            comment = self.compute_ras()
            return comment

        comment = self.compute_others(id_area)

        if risk_min == risk_max:
            comment = self.compute_global_idem(id_area)

        elif (
            (len(risk_period_max.values) == 1)
            and (risk_min == 0)
            and (len(set(da_val)) == 2)
        ):
            # print("compute_pic(id_area)")
            comment = self.compute_pic(id_area)

        elif (
            (risk_min == 0)
            and (len(list(set(da_val))) == 2)
            and (len(self.start_stop_echeances(risk_period_max)) == 1)
        ):
            comment = self.compute_global_idem(id_area)

        elif (
            (risk_min != 0)
            and (risk_min != risk_max)
            and (not comparison_desc.all())
            and (not comparison_asc.all())
        ):
            # print("compute_global(id_area)")
            comment = self.compute_global(id_area)

        elif comparison_desc.all():
            list_bool = []
            for i in range(len(da_val) - 1):
                if (da_val[i] != da_val[i + 1]) and (da_val[i + 1] == da_val[i] - 1):
                    list_bool.append(True)
                elif (da_val[i] != da_val[i + 1]) and (da_val[i + 1] != da_val[i] - 1):
                    list_bool.append(False)

            if set(list_bool) == {True}:
                if risk_min != 0:
                    if (
                        len(self.component.get_nb_evts([risk_max, risk_min])) == 1
                        and self.component.get_nb_evts([risk_max, risk_min])[0] == 1
                    ):
                        # print("compute_decroissance(id_area)")
                        comment = self.compute_decroissance(id_area)
                elif (risk_min == 0) and (weatherVarName in list_precip):
                    if (
                        len(self.component.get_nb_evts([risk_max, risk_min])) == 1
                        and self.component.get_nb_evts([risk_max, risk_min])[0] == 1
                    ):
                        # print("compute_decroissance_pluie(id_area)")
                        comment = self.compute_decroissance_pluie(id_area)
            else:
                if risk_min != 0:
                    # print("compute_global(id_area)")
                    comment = self.compute_global(id_area)

        elif comparison_asc.all() and risk_min != 0:
            list_bool = []
            for i in range(len(da_val) - 1):
                if (da_val[i] != da_val[i + 1]) and (da_val[i + 1] == da_val[i] + 1):
                    list_bool.append(True)
                elif (da_val[i] != da_val[i + 1]) and (da_val[i + 1] != da_val[i] + 1):
                    list_bool.append(False)

            if set(list_bool) == {True}:
                if risk_min != 0:
                    if (
                        len(self.component.get_nb_evts([risk_max, risk_min])) == 1
                        and self.component.get_nb_evts([risk_max, risk_min])[0] == 1
                    ):
                        # print("self.compute_croissance(id_area)")
                        comment = self.compute_croissance(id_area)
            else:
                if risk_min != 0:
                    # print("compute_global(id_area)")
                    comment = self.compute_global(id_area)

        elif len(set(da_val)) == 3:
            if (
                (len(self.start_stop_echeances(risk_period_max)) == 1)
                and (len(self.start_stop_echeances(risk_period_other)) == 1)
                and (risk_min == 0)
            ):
                # print("compute_palier_different_levels(id_area)")
                comment = self.compute_palier_different_levels(id_area)

        return comment
