from math import log, sqrt
from typing import List, NoReturn

import numpy as np
from tabulate import tabulate


class DescriptiveTable:

    """Geração de dados da tebela descritiva.

    exemple:
    from ifrn_estatistica.descriptive_table import DescriptiveTable


    table = DescriptiveTable(dataset, 3)
    table.generate_table()
    """

    def __init__(self, dataset: List, decimal_places: int):

        """Inicia o obj com uma dataset e define as casas decimais.

        :param dataset: lista com os dados a serem processados
        :param decimal_places: número de casas decimais
        """

        self.dataset = dataset
        self.decimal_places = decimal_places
        self._table = {}
        self._number_classes = self.sturges_rule()
        self._amplitude = self.amplitude_classes()

    def amplitude_classes(self) -> int:
        """Método para retornar a amplitude de classes.

        :return: int
        """

        at = max(self.dataset) - min(self.dataset)
        return round(at / self._number_classes)

    def sturges_rule(self) -> int:

        """Método para retornar a numero de classes.

        :return: int
        """
        return round(1 + 3.322 * log(len(self.dataset), 10))

    def classes(self) -> List:
        """Método para geração das classes da tabela descritiva.

        :return: list
        """
        limite_inferior = min(self.dataset)
        classes = []
        for _ in range(1, self._number_classes + 1):
            classes.append(
                (
                    round(limite_inferior, self.decimal_places),
                    round(
                        (limite_inferior + self._amplitude),
                        self.decimal_places,
                    ),
                ),
            )
            limite_inferior += self._amplitude
        self._table["Classes"] = classes
        return classes

    def simple_frequency(self) -> List:
        """Método para geração do frequencia simples "fi".

        :return: list
        """
        classes = self.classes()
        fi = list()
        count_fi = 0
        for i in range(self._number_classes):
            for j in range(len(self.dataset)):
                if (
                    self.dataset[j] >= classes[i][0]
                    and self.dataset[j] < classes[i][1]
                ):
                    count_fi += 1
            fi.append(count_fi)
            count_fi = 0
        self._table["fi"] = fi
        return fi

    def cumulative_frequency(self) -> List:
        """Método para geranção a frequencia acumulada.

        :return: list
        """
        fi = self.simple_frequency()
        Fi = list()
        for i in range(self._number_classes):
            if not i:
                Fi.append(fi[i])
            else:
                Fi.append((Fi[-1] + fi[i]))
        self._table["Fi"] = Fi
        return Fi

    def simple_relative_frequency(self) -> List:
        """Método para geração da frequencia relativa simples "fri".

        :return: list
        """
        fi = self.simple_frequency()
        fri = list()
        for i in range(self._number_classes):
            fri.append((round(fi[i] / len(self.dataset), self.decimal_places)))
        self._table["fri"] = fri
        return fri

    def cumulative_relative_frequency(self) -> List:

        """Método para retorno da frenquencia relativa acumulada "Fri".

        :return: list
        """
        fi = self.simple_frequency()
        fri = self.simple_relative_frequency()
        Fri = list()
        for i in range(self._number_classes):
            if not i:
                Fri.append(
                    (round(fi[i] / len(self.dataset), self.decimal_places))
                )
            else:
                Fri.append((round((fri[i] + Fri[-1]), self.decimal_places)))
        self._table["Fri"] = Fri
        return Fri

    def middle_point(self) -> List:
        """Método para geração dos pontos médios.

        :return: list
        """
        classes = self.classes()
        xi = list()
        for i in range(self._number_classes):
            xi.append(
                round((classes[i][0] + classes[i][1]) / 2, self.decimal_places)
            )
        self._table["XI"] = xi
        return xi

    def percentage(self) -> List:
        """Método para geração do percentual "%".

        :return: list
        """
        fri = self.simple_relative_frequency()
        percentage_values = []
        for i in range(self._number_classes):
            percentage_values.append(
                (round((fri[i] * 100), self.decimal_places))
            )

        self._table["%"] = percentage_values
        return percentage_values

    def angle(self) -> List:
        """Método para geração dos angulos "Ang".

        :return: list
        """
        Fri = self.cumulative_relative_frequency()
        angle_values = list()
        for i in range(self._number_classes):
            angle_values.append(round((Fri[i] * 360), self.decimal_places))
        self._table["Ang"] = angle_values
        return angle_values

    def fci(self) -> List:
        """Método para geração de valores para grafico suavisado.

        :return: list
        """
        fi = self.simple_frequency()
        fci = list()
        for i in range(self._number_classes):
            if not i:
                fci.append(((2 * fi[i]) + fi[(i + 1)]) / 4)
            else:
                try:
                    fci.append(((fi[(i - 1)] + (2 * fi[i]) + fi[(i + 1)]) / 4))
                except IndexError:
                    fci.append((fi[(i - 1)] + 2 * fi[i]) / 4)
        self._table["FCI"] = fci
        return fci

    def weighted_average(self):
        """Método para retorno de XIFI.

        :return: list
        """
        xi = self.middle_point()
        fi = self.simple_frequency()
        xifi = list()
        for i in range(self._number_classes):
            xifi.append(round(xi[i] * fi[i], self.decimal_places))
        self._table["XIFI"] = xifi
        return xifi

    def deviation(self) -> float:
        """Método para geração do desvio.

        :return: list
        """
        xi = self.middle_point()
        x = self.get_average()
        v0 = []
        for i in range(len(xi)):
            v0.append(round(abs((xi[i] - x)), self.decimal_places))
        self._table["|X - XI|"] = v0
        return v0

    def deviation_v1(self) -> float:
        """Método para geração de deviation_V1

        :return: list
        """
        v0 = self.deviation()
        v1 = []
        for i in range(len(v0)):
            v1.append(np.around((v0[i] ** 2), decimals=self.decimal_places))
        self._table["(X - XI)²"] = v1
        return v1

    def deviation_v2(self) -> List:
        """Método para o retorno de deviation_V2

        :return: list
        """
        fi = self.simple_frequency()
        v1 = self.deviation_v1()
        v2 = []
        for i in range(len(fi)):
            v2.append(np.around((v1[i] * fi[i]), decimals=self.decimal_places))
        self._table["(X - XI)²*fi"] = v2
        return v2

    def get_varience(self, sample=True) -> List:
        """Método para geração da variancia.
        :param sample: default true para calcular a variancia amostral
        :return: list
        """
        fi_sum = (
            (sum(self.simple_frequency()) - 1)
            if sample
            else sum(self.simple_frequency())
        )
        v2_sum = sum(self.deviation_v2())
        variance = round((v2_sum / fi_sum), self.decimal_places)
        self._table["Variância"] = [variance]
        return variance

    def standard_deviation(self) -> float:
        """Método para geração do desvio padrão.

        :return: list
        """
        variance = self.get_varience()
        std_dev = round(sqrt(variance), self.decimal_places)
        self._table["Desvio Padrão"] = [std_dev]
        return std_dev

    def get_average(self) -> float:
        """Método para calculara média.

        :return: float
        """
        xifi = self.weighted_average()
        average = round(sum(xifi) / len(self.dataset), self.decimal_places)
        self._table["Media"] = [average]
        return average

    def get_moda(self) -> float:
        """Método para geração da moda.

        :return: float
        """
        classes = self.classes()
        fi = self.simple_frequency()
        modal_number = round(
            sum(self.weighted_average()) / len(self.dataset),
            self.decimal_places,
        )
        moda = 0
        for i in range(self._number_classes):
            if modal_number >= classes[i][0] and modal_number <= classes[i][1]:
                previous_fi = fi[(i - 1)] if i else 0
                later_fi = (
                    fi[(i + 1)] if i == (self._number_classes - 1) else 0
                )
                # moda = classes[i][0] + ((fi[i] - previous_fi)/((fi[i] - previous_fi) + (fi[i] - later_fi)))*self.amplitude_classes()
                moda = (
                    classes[i][0]
                    + (
                        (fi[i] - previous_fi)
                        / ((2 * fi[i]) - (previous_fi + later_fi))
                    )
                    * self.amplitude_classes()
                )

        self._table["MODA"] = [moda]
        return round(moda, self.decimal_places)

    def get_median(self) -> float:
        """Método para geração de médiana

        :return: float
        """
        classes = self.classes()
        fi = self.simple_frequency()
        h = self._amplitude
        Fi = self.cumulative_frequency()
        range_fi = sum(fi) / 2
        median = 0
        for i in range(len(Fi)):
            if not i:
                if range_fi <= Fi[i]:
                    median = classes[i][0] + ((range_fi / fi[i]) * h)
            if range_fi >= (Fi[(i - 1)] + 1) and range_fi <= Fi[i]:
                median = classes[i][0] + (
                    ((range_fi - Fi[(i - 1)]) / fi[i]) * h
                )

        self._table["Mediana"] = [round(median, self.decimal_places)]
        return round(median, self.decimal_places)

    def generate_table(self) -> NoReturn:
        """Método para geração da tabela descritiva.

        :return: None
        """
        print(tabulate(self._table, headers="keys", tablefmt="fancy_grid"))

    def __repr__(self):
        return "Classe DescriptiveTable"
