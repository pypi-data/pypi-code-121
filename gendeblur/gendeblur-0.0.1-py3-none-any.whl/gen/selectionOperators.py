import random
import copy

class SelectionOperators(object):
    @staticmethod
    def __select_random(individuals, k):
        """
        Выбрать k случайных особей
        :param individuals: особои
        :param k: количество особей для выбора
        :returns: выбранные особи в виде списка
        """
        return [random.choice(individuals) for i in range(k)]

    @staticmethod
    def __select_tournament(individuals, k, tournsize=2):
        """
        Турнирная селекция
        :param individuals: особи
        :param k: количество особей для выбора
        :param tournsize: размер турнира
        :return: отобранные особи
        """
        chosen = []
        for i in range(k):
            aspirants = SelectionOperators.__select_random(individuals, tournsize)
            chosen.append(copy.deepcopy(max(aspirants, key=lambda ind: ind.score)))
        return chosen

    @staticmethod
    def select(individuals, selection_args):
        try:
            type = selection_args["type"]
            k = selection_args["k"]
            if not isinstance(type, str) and not isinstance(k, int):
                raise AttributeError("Selection type should be string")
        except KeyError:
            raise AttributeError("Define selection type")

        # Свитчим вид селекции
        if type == "tournament":
            try:
                tournsize = selection_args['tournament_size']
                if not isinstance(tournsize, int):
                    raise AttributeError("Wrong types of arguments")
                return SelectionOperators.__select_tournament(individuals, k, tournsize)
            except KeyError:
                raise AttributeError("Pass tournsize (int)")
        elif type == "random":
            return SelectionOperators.__select_random(individuals, k)
