# hp_set.py: helper class for formatting hp_set hyperparameters
import json

class HpSetFormatter():

    def __init__(self):
        self.simple_set_names = {}
        self.changed_set_names = {}
        self.hp_common_set = {}
        self.hp_change_set = {}

    def parse_and_sort_hp_set(self, value):
        # fix up to be legal json
        hp_set_str = value.replace("'", '"')
        hp_set = json.loads(hp_set_str)

        # sort by hp names
        keys = list(hp_set)
        keys.sort()
        hp_set = {key:hp_set[key] for key in keys}

        return hp_set

    def get_changed_hp_set(self, value):
        value = self.parse_and_sort_hp_set(value)
        value = str(value)

        new_value = self.changed_set_names[value]
        return new_value

    def format_hpset_simple(self, value):
        value = self.parse_and_sort_hp_set(value)
        value = str(value)

        if value not in self.simple_set_names:
            self.simple_set_names[value] = "hp_set_" + str(1 + len(self.simple_set_names))

        new_value = self.simple_set_names[value]
        return new_value


    def format_hpset_changed(self, value):
        value = self.parse_and_sort_hp_set(value)
        value = str(value)

        # if value not in self.hp_set_names:
        #     self.hp_set_names[value] = "hp_set_" + str(1 + len(self.hp_set_names))

        new_value = self.changed_set_names[value]
        return new_value

    def build_hp_set_names(self, records):
        '''
        builds a dict of only the hparam name/values that change between hp_sets
        '''
        hp_values = {}
        hp_changed = {}
        hp_sets = []
        first_set = True

        for record in records:
            if "hp_set" in record:

                hp_set_str = record["hp_set"]
                hp_set = self.parse_and_sort_hp_set(hp_set_str)
                hp_sets.append(hp_set)

                if first_set:
                    # process the first hp_set seen
                    hp_values = dict(hp_set)
                    first_set = False

                else:
                    # process an hp_set (not the first one seen)
                    needed = {key:1 for key in hp_values}

                    for hp,value in hp_set.items():

                        if not hp in hp_values:
                            # new hyperparamer
                            hp_values[hp] = value
                            hp_changed[hp] = 1

                        else:
                            # found known hyperparameter
                            needed[hp] = 0
                            if hp_values[hp] != value:
                                # new value found for this hp
                                hp_changed[hp] = 1

                    for hp, value in needed.items():
                        if value:
                            # this set was missing the hp 
                            hp_changed[hp] = 1


        # build map of each hp_set (from its full name to its compressed, changes-only name)
        hp_set_names = {}

        for hp_set in hp_sets:
            min_hp_set = {hp:value for hp,value in hp_set.items() if hp in hp_changed}
            hp_set_names[str(hp_set)] = min_hp_set

        self.changed_set_names = hp_set_names

        # compute the common hyperparameters (those that didn't change)
        self.hp_common_set = {hp:value for hp,value in hp_values.items() if hp not in hp_changed}
        self.hp_change_set = {hp:value for hp,value in hp_values.items() if hp in hp_changed}

