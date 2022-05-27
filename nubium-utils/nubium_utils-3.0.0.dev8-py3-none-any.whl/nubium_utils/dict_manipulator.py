from box import Box
from functools import reduce
from copy import deepcopy


class DictManipulator(Box):

    def __init__(self, *args, **kwargs):
        kwargs.update({'box_dots': True})
        super().__init__(*args, **kwargs)

    @staticmethod
    def _apply_funcs(funcs, str_value):
        """
        Perform a given list of functions in succession that each take one argument and return one value.
        Typically used for combining multiple string manipulations.
        """
        if isinstance(funcs, list):
            return reduce(lambda result, f: f(result), funcs, str_value)
        else:
            return funcs(str_value)

    def apply_func_dict_to_field(self, field_path, func_dict):
        """
        DOES *IN-PLACE* MODIFICATION ON SELF.
        Perform all functions in a func_dict where each k,v pair is - func: kw_arg_dict (for func).
        The first arg of those function(s) should be a desired string to operate on; in this case, a key path on self.
        """
        self[field_path] = reduce(lambda result, f_key: f_key(result, **func_dict[f_key]), func_dict, self[field_path])

    def _apply_funcs_to_mask_selection(self, dict_self, mask, funcs):
        """
        the actual workhorse of its non-underscored counterpart; allows you to use a recursive function on self.
        """
        for k, v in mask.items():
            if isinstance(v, dict):
                 self._apply_funcs_to_mask_selection(dict_self[k], v, funcs)
            else:
                dict_self[k] = self._apply_funcs(funcs, dict_self[k])

    def apply_funcs_to_mask_selection(self, mask, funcs):
        """
        DOES *IN-PLACE* MODIFICATION ON SELF.
        Apply a list of functions to each value based on the respective keys in the "mask".
        :param mask: a direct dict subset of self (nests and all) with all values as NoneTypes
        :type mask: dict
        :param funcs: functions to apply to each DictManipulator field based on the fields given via the mask
        :type funcs: list or func
        """
        self._apply_funcs_to_mask_selection(self, mask, funcs)

    @staticmethod
    def _check_if_nulled(old_str_value, new_str_value):
        """
        Method that checks if a value was newly nullified with respect to a previous version of it;
        if so, keep the previous version.
        """
        if old_str_value and not new_str_value:
            return old_str_value
        return new_str_value

    def _compare_and_overwrite_nulled_values(self, dict_self, original_dict):
        """
        the actual workhorse of its non-underscored counterpart; allows you to use a recursive function on self.
        """
        for k, v in original_dict.items():
            if isinstance(v, dict):
                 self._compare_and_overwrite_nulled_values(dict_self[k], v)
            else:
                dict_self[k] = self._check_if_nulled(v, dict_self[k])

    def compare_and_overwrite_nulled_values(self, original_dict):
        """
        DOES *IN-PLACE* MODIFICATION ON SELF.
        Method that checks if any fields on self were newly nullified with respect to a provided previous version of it;
        if so, keep the previous version's non-null value for that respective field.
        :param original_dict: the previous version of self to compare against
        :type original_dict: dict
        """
        self._compare_and_overwrite_nulled_values(self, original_dict)

    def _view_populated_mask(self, dict_self, mask):
        """
        the actual workhorse of its non-underscored counterpart; allows you to use a recursive function on self.
        """
        return {k: self._view_populated_mask(dict_self[k], v) if isinstance(v, dict) else dict_self[k] for k, v in mask.items()}

    def view_populated_mask(self, mask):
        """
        DOES *NOT* MODIFY SELF.
        Returns you a populated version of the provided mask with based on self's current values for those fields.
        Does not alter self in any manner.
        :param mask: a direct dict subset of self (nests and all) with all values as NoneTypes
        :type mask: dict
        :return: the populated mask
        :rtype: dict
        """
        return self._view_populated_mask(self, mask)

    def view_while_ignoring_fields(self, ignore_field_list):
        """
        DOES *NOT* MODIFY SELF.
        A way of returning self with some keys removed from the dict.
        :param ignore_field_list: list of tuples, where each tuple is one full key traversal to a value;
        ex [('key_nest1', 'key_nest2')] would remove dict['key_nest1']['key_nest2']
        :return: self with the desired removed keys
        :rtype: dict
        """
        x = deepcopy(self)
        for item in ignore_field_list:
            temp = x
            for nest in item[:-1]:
                temp = temp[nest]
            del temp[item[-1]]
        return x
