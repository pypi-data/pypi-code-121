"""
@package text.comment.__init__

Module for representative value in detailed comment
"""

# Standard packages
import re
import numpy as np

# Own package
from mfire.settings import PREFIX_TO_VAR, Settings, TEMPLATES_FILENAMES
from mfire.settings import get_logger
from mfire.utils.formatter import get_synonym
from mfire.composite.operators import ComparisonOperator
from mfire.text.template import Template, read_file
from mfire.text.comment.component import ComponentInterface
from mfire.text.comment.comment_builder import CommentBuilder


# Logging
LOGGER = get_logger(
    name="text.representative_builder.mod", bind="text.representative_builder"
)


NO_VALUE = -999999


class RepresentativeValueManager(CommentBuilder):
    """
    This class enable to manage all text for representative values.
    It chooses which class needs to be used for each case.
    """

    @staticmethod
    def get_prefix(variable):
        """
        Return only the first carachter of the variable
        It is enough to identify the variable.
        It is no longer necessary to have a full list of all possibilities.
        """
        prefix = variable.split("_")[0]
        pattern = r"[0-9]"
        prefix = re.sub(pattern, "", prefix)
        return prefix

    def process_value(self) -> None:
        """
        On process les différentes valeurs représentatives.
        S'il n'y en a pas, théoriquement on ne fait rien.
        Chaque valeur rerépsentative est processée.
        """
        dict_value = self.component_handler.get_critical_value()
        # Pour l'instant on ajoute une phrase pour chacune des variables présente.
        # Chaque phrase est construite de la même manière.
        for key in dict_value:
            prefix = self.get_prefix(key)
            if prefix == "FF":
                value_builder = FFBuilder()
            elif prefix == "RAF":
                value_builder = FFRafBuilder()
            elif prefix == "T":
                value_builder = TemperatureBuilder()
            elif prefix in ["PRECIP", "EAU"]:
                value_builder = PrecipBuilder()
            elif prefix == "NEIPOT":
                value_builder = SnowBuilder()
            else:
                LOGGER.error("We don't know how to speak about this parameter.")
                value_builder = ""
            self.comment += value_builder.add_variable_value(key, dict_value[key])

    def process(self, component_handler: ComponentInterface) -> None:
        """process: creates and processes a new detailed comment, accessible
        through the self.comment property

        Args:
            component_handler (ComponentInterface): Component for which
                the detailed comment is being processed.
        """
        super().process(component_handler)
        self.process_value()


class RepresentativeValueBuilder(CommentBuilder):
    """
    This class enable to speak about representative values
    """

    cumul_var = ["NEIPOT", "PRECIP", "EAU"]
    intro_var = ""
    var_d = ""

    feminin = False
    template_retriever = read_file(
        TEMPLATES_FILENAMES[Settings().language]["multizone"]["rep_val"]
    )
    seed = None  # Permettra de fixer la seed pour des tests

    environ_list = ["aux alentours de"]

    @staticmethod
    def get_prefix(variable):
        prefix = variable.split("_")[0]
        pattern = r"[0-9]"
        prefix = re.sub(pattern, "", prefix)
        return prefix

    def get_accum(self, variable):
        """
        Permet d'avoir le nombre d'heure sur lequel la variable est cumulé.

        Args:
            variable (str): Le nom de la variable

        Returns:
            [str]: le nombre d'heure sur lequel la variable est cumulée
        """
        full_prefix = variable.split("_")[0]
        prefix = self.get_prefix(variable)
        accum = full_prefix.replace(prefix, "")
        if int(accum) > 1:
            accum_text = str(accum) + " heures"
        else:
            accum_text = str(accum) + " heure"
        return accum, accum_text

    def get_var_type(self, variable):
        """
        Récupère le type de variable à partir du nom complet.
        """
        prefix = self.get_prefix(variable)
        res = PREFIX_TO_VAR.get(prefix, "unknown")
        return res

    def get_variable_intro(self, variable):
        """
        Récupère la manière de parler de la variable
        """
        return self.intro_var

    def get_variable_d(self, variable):
        """
        Permet d'avoir la variable (commençant par d)

        Args:
            variable (str): La variable (pas utilisé ici mais dans des classes filles)

        Returns:
            (str): Le choix pour la variable
        """
        return self.var_d

    def environ(self):
        """
        Choisi comment dire environ
        """
        # rng = np.random.default_rng(self.seed)
        # return rng.choice(self.environ_list)
        return get_synonym(self.environ_list[0]) + " "

    @staticmethod
    def units(unit):
        """
        On récupère l'unité. Si elle est à None on met un blanc.
        """
        res = ""
        if unit is not None:
            res = unit
        return res

    def get_format(self, variable):
        """
        On récupère les informations qui sont potentiellement utilisé dans les phrases.
        """
        format_table = {}
        format_table["var"] = self.get_variable_intro(variable)
        format_table["var_d"] = self.get_variable_d(variable)
        if self.feminin:
            format_table["feminin"] = "e"
        else:
            format_table["feminin"] = ""
        format_table["environ"] = self.environ()
        return format_table

    def get_sentence(self, variable, sentence_type):
        """
        Choix de la phrase de base.
        """
        default = (
            f"Echec dans la récupération du template"
            f"(key={sentence_type}) (error COM-001)."
        )
        sentence = self.template_retriever.get(key=sentence_type, default=default)
        return Template(sentence)

    @staticmethod
    def rounding(x, **kwargs):
        """
        Fonction spécifique à implémenter pour chaque variable.
        """
        return x

    @staticmethod
    def modify_environ(format_table, rep_value, sentence):
        if str(rep_value).startswith("au"):
            format_table["environ"] = "d'"
            sentence = sentence.replace("{environ} ", " {environ}")
        elif str(rep_value).startswith("de"):
            format_table["environ"] = ""
        return sentence

    @staticmethod
    def replace_critical(dict_in):
        if dict_in.get("next_critical", None) is not None and ComparisonOperator(
            dict_in["operator"]
        )(dict_in["value"], dict_in["next_critical"]):
            rep_value = (
                dict_in["next_critical"]
                + (dict_in["next_critical"] - dict_in["value"]) / 100
            )
            local = dict_in["value"]
            LOGGER.debug(
                f"On remplace la valeur critique {local} {rep_value} {dict_in}"
            )
        else:
            rep_value = dict_in["value"]
            local = None
        return (rep_value, local)

    def identify_case(self, variable: str, dict_in: dict):
        """
        Cette fonction identifie le cas a traiter.
        Elle commence à remplir le tableau.

        Args:
            variable (str): La variable d'intérêt
            dict_in (dict): Le dictionnaire
        """
        speak = None
        local_plain = None
        local_mountain = None
        rep_plain = None
        format_table = self.get_format(variable)
        if "plain" in dict_in:
            rep_value, local = self.replace_critical(dict_in["plain"])
            rep_plain = self.rounding(
                rep_value,
                operator=dict_in["plain"]["operator"],
                environ=format_table["environ"],
            )
            if local is not None:
                local_plain = self.rounding(
                    local,
                    operator=dict_in["plain"]["operator"],
                    environ=format_table["environ"],
                )
                if local_plain == rep_plain:
                    local_plain = None
                else:
                    format_table["local_value"] = " ".join(
                        [str(local_plain), self.units(dict_in["plain"]["units"])]
                    )
            else:
                local_plain = None
            format_table["value"] = " ".join(
                [str(rep_plain), self.units(dict_in["plain"]["units"])]
            )

            speak = "plain"

        if "mountain" in dict_in:
            rep_value, local = self.replace_critical(dict_in["mountain"])
            # On regarde si la condition est remplie sur la montagne
            rep_mountain = self.rounding(
                rep_value,
                operator=dict_in["mountain"]["operator"],
                environ=format_table["environ"],
            )
            format_table["mountain_value"] = " ".join(
                [str(rep_mountain), self.units(dict_in["mountain"]["units"])]
            )
            format_table["hauteur"] = "sur les hauteurs"

            if local is not None:
                local_mountain = self.rounding(
                    local,
                    operator=dict_in["mountain"]["operator"],
                    environ=format_table["environ"],
                )
                if local_mountain == rep_mountain:
                    local_mountain = None
                else:
                    format_table["local_mountain_value"] = " ".join(
                        [str(local_mountain), self.units(dict_in["mountain"]["units"])]
                    )
            else:
                local_mountain = None

            if rep_plain is not None:
                # On reprend ce qui etait dans le module de Lamyaa
                if rep_plain != rep_mountain or (
                    local_mountain is not None and local_mountain != local_plain
                ):
                    speak = "plain_mountain"
                else:
                    speak = "plain"
            else:
                speak = "mountain"

        return (speak, format_table, local_plain, local_mountain)

    def add_variable_value(self, variable: str, dict_in: dict):
        """
        Pour la variable en question, on va voir si on parle que de la valeur sur
        la plaine ou  de la valeur sur la plaine et de la valeur en montagne.
        Pour l'instant la phrase est la même qu'il y ai une ou plusieurs variables.
        """
        speak, format_table, local_plain, local_mountain = self.identify_case(
            variable, dict_in
        )
        # On va maitnenant faire un arbre de décision pour savoir le type de
        # phrase à charger.

        if speak == "plain" and local_plain is None:
            sentence_type = "plain"
        elif speak == "plain" and local_plain is not None:
            sentence_type = "local_plain"
        elif speak == "mountain" and local_mountain is None:
            sentence_type = "mountain"
        elif speak == "mountain" and local_mountain is not None:
            sentence_type = "local_mountain"
        elif (
            speak == "plain_mountain" and local_plain is None and local_mountain is None
        ):
            sentence_type = "plain_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is not None
            and local_mountain is None
        ):
            sentence_type = "local_plain_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is None
            and local_mountain is not None
        ):
            sentence_type = "plain_local_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is not None
            and local_mountain is not None
        ):
            sentence_type = "local_plain_local_mountain"

        sentence = self.get_sentence(variable, sentence_type)
        sentence = self.modify_environ(format_table, format_table["value"], sentence)
        return sentence.format(**format_table)


class FFBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour le vent
    """

    feminin = False
    intro_var = "le vent"
    var_d = "un vent"

    @staticmethod
    def rounding(x, **kwargs):
        """
            Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
            Exemples:
                Input --> Output
                 42   -->  40 à 45
                 39   -->  35 à 40
        """
        res = None
        if x is not None:
            start = (int(x / 5)) * 5
            end = (int(x / 5)) * 5 + 5
            res = str(start) + " à " + str(end)
        return res


class TemperatureBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour la température
    """

    feminin = True
    intro_var = "la température"
    var_d = "une température"

    @staticmethod
    def rounding(x, operator="<", **kwargs):
        """
        On prend la valeur inférieure ou supérieur selon les cas.
        """
        if operator in ["<", "<=", "inf", "infegal"]:
            res = int(np.floor(x))
        else:
            res = int(np.ceil(x))
        return str(res)


class FFRafBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour le vent
    """

    feminin = True
    intro_var = "les rafales"
    var_d = "des rafales"
    environ_list = ["de l'ordre de"]

    template_retriever = read_file(
        TEMPLATES_FILENAMES[Settings().language]["multizone"]["rep_val_FFRaf"]
    )

    @staticmethod
    def rounding(x, **kwargs):
        """
            Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
            Exemples:
                Input --> Output
                 42   -->  40 à 45
                 39   -->  35 à 40
        """
        res = None
        if x is not None:
            start = (int(x / 10)) * 10
            end = (int(x / 10)) * 10 + 10
            res = str(start) + " à " + str(end)
            if kwargs.get("environ", None) == "comprises entre":
                res = res.replace("à", "et")
        return res


class SnowBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour la neige
    """

    feminin = False

    def get_variable_intro(self, variable):
        """
        Récupère la manière de parler de la variable
        """
        _, accum_text = self.get_accum(variable)
        res = f"le potentiel de neige sur {accum_text}"
        return res

    def get_variable_d(self, variable):

        _, accum_text = self.get_accum(variable)
        res = f"un potentiel de neige sur {accum_text}"
        return res

    def get_str_no_value(self, dict_in):
        if "plain" in dict_in:
            no_value = " ".join([str(NO_VALUE), self.units(dict_in["plain"]["units"])])
        else:
            LOGGER.debug(f"Pas possible de prendre l'unite sur la plaine {dict_in}")
            no_value = " ".join(
                [str(NO_VALUE), self.units(dict_in["mountain"]["units"])]
            )
        return no_value

    def identify_case(self, variable: str, dict_in: dict):
        (speak, format_table, local_plain, local_mountain) = super().identify_case(
            variable, dict_in
        )
        no_value = self.get_str_no_value(dict_in)
        if format_table.get("value", None) == no_value:
            speak = "mountain"
        elif format_table.get("mountain_value", None) == no_value:
            speak = "plain"
        return (speak, format_table, local_plain, local_mountain)

    def add_variable_value(self, variable: str, dict_in: dict):
        """
        Pour la variable en question, on va voir si on parle que de la valeur sur
        la plaine ou  de la valeur sur la plaine et de la valeur en montagne.
        Pour l'instant la phrase est la même qu'il y ai une ou plusieurs variables.
        """
        speak, format_table, local_plain, local_mountain = self.identify_case(
            variable, dict_in
        )
        no_value = self.get_str_no_value(dict_in)
        # On va maitnenant faire un arbre de décision pour savoir le type de
        # phrase à charger.
        if (
            speak == "plain"
            and local_plain is None
            and format_table["value"] not in [None, no_value]
        ):
            sentence_type = "plain"
        elif (
            speak == "plain"
            and local_plain is not None
            and format_table["value"] not in [None, no_value]
        ):
            sentence_type = "local_plain"
        elif (
            speak == "mountain"
            and format_table["mountain_value"] not in [None, no_value]
            and local_mountain is None
        ):
            sentence_type = "mountain"
        elif (
            speak == "mountain"
            and format_table["mountain_value"] not in [None, no_value]
            and local_mountain is not None
        ):
            sentence_type = "local_mountain"
        elif (
            speak == "plain_mountain" and local_plain is None and local_mountain is None
        ):
            sentence_type = "plain_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is not None
            and local_mountain is None
        ):
            sentence_type = "local_plain_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is None
            and local_mountain is not None
        ):
            sentence_type = "plain_local_mountain"
        elif (
            speak == "plain_mountain"
            and local_plain is not None
            and local_mountain is not None
        ):
            sentence_type = "local_plain_local_mountain"
        else:
            sentence_type = None

        if sentence_type is not None:
            sentence = self.get_sentence(variable, sentence_type)
            sentence = sentence.format(**format_table)
        else:
            sentence = ""
            LOGGER.error(
                "Pour la neige, on ne tombe pas dans un bon cas. Revoir pourquoi."
            )
        return sentence

    @staticmethod
    def rounding(x, **kwargs):
        """
            Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
            Exemples:
                Input --> Output
                 42   -->  40 à 45
                 39   -->  35 à 40
        """
        if x is None:
            res = None
        elif x < 1e-6:
            LOGGER.debug("A true 0 is found {x}.")
            res = NO_VALUE
        elif x < 1:
            res = "0 à 1"
        elif x < 3:
            res = "1 à 3"
        elif x < 5:
            res = "3 à 5"
        elif x < 7:
            res = "5 à 7"
        elif x < 10:
            res = "7 à 10"
        elif x < 15:
            res = "10 à 15"
        elif x < 20:
            res = "15 à 20"
        else:
            start = (int(x / 10)) * 10
            end = (int(x / 10)) * 10 + 10
            res = str(start) + " à " + str(end)
        return res


class PrecipBuilder(RepresentativeValueBuilder):
    """
    Classe spécifique pour les précipitations
    """

    feminin = False

    def get_variable_intro(self, variable):
        """
        Récupère la manière de parler de la variable
        """
        prefix = self.get_prefix(variable)
        _, accum_text = self.get_accum(variable)
        if prefix == "PRECIP":
            res = f"le cumul de précipitation sur {accum_text}"
        elif prefix == "EAU":
            res = f"le cumul de pluie sur {accum_text}"
        else:
            LOGGER.error(f"Prefix unknown. Get {prefix}")
        return res

    def get_variable_d(self, variable):
        prefix = self.get_prefix(variable)
        _, accum_text = self.get_accum(variable)
        if prefix == "PRECIP":
            res = f"un cumul de précipitation sur {accum_text}"
        elif prefix == "EAU":
            res = f"un cumul de pluie sur {accum_text}"
        else:
            LOGGER.error(f"Prefix unknown. Get {prefix}")
        return res

    @staticmethod
    def rounding(x, **kwargs):
        """
            Foncion pour arrondir les valeurs à l'intervalle de  5 le plus proche.
            Exemples:
                Input --> Output
                 42   -->  40 à 45
                 39   -->  35 à 40
        """
        if x is None:
            res = None
        elif x < 3:
            res = "au maximum 3"
        elif x < 7:
            res = "3 à 7"
        elif x < 10:
            res = "7 à 10"
        elif x < 15:
            res = "10 à 15"
        elif x < 20:
            res = "15 à 20"
        elif x < 25:
            res = "20 à 25"
        elif x < 30:
            res = "25 à 30"
        elif x < 40:
            res = "30 à 40"
        elif x < 50:
            res = "40 à 50"
        elif x < 60:
            res = "50 à 60"
        elif x < 80:
            res = "60 à 80"
        elif x < 100:
            res = "80 à 100"
        else:
            start = (int(x / 50)) * 50
            end = (int(x / 50)) * 50 + 50
            res = str(start) + " à " + str(end)
        return res
