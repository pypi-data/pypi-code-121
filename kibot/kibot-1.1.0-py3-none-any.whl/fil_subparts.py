# -*- coding: utf-8 -*-
# Copyright (c) 2021 Salvador E. Tropea
# Copyright (c) 2021 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
"""
Implements the KiCost subparts mechanism.
The 'manf#' field can contain more than one value separated by ;
The result is REF#subpart
"""
import re
from copy import deepcopy
from .gs import GS
from .optionable import Optionable
from .misc import W_NUMSUBPARTS, W_PARTMULT, DISTRIBUTORS_F
from .macros import macros, document, filter_class  # noqa: F401
from . import log


logger = log.get_logger()


class DistributorsList(Optionable):
    _default = DISTRIBUTORS_F


@filter_class
class Subparts(BaseFilter):  # noqa: F821
    """ Subparts
        This filter implements the KiCost subparts mechanism """
    def __init__(self):
        super().__init__()
        self._is_transform = True
        with document:
            self.check_multiplier = Optionable
            """ [list(string)] List of fields to include for multiplier computation.
                If empty all fields in `split_fields` and `manf_pn_field` are used """
            self.manf_field = 'manf'
            """ Field for the manufacturer name """
            self.manf_pn_field = 'manf#'
            """ Field for the manufacturer part number """
            self.modify_value = True
            """ Add '- p N/M' to the value """
            self.modify_first_value = True
            """ Modify even the value for the first component in the list (KiCost behavior) """
            self.multiplier = True
            """ Enables the subpart multiplier mechanism  """
            self.mult_separators = ':'
            """ Separators used for the multiplier. Each character in this string is a valid separator """
            self.ref_sep = '#'
            """ Separator used in the reference (i.e. R10#1) """
            self.separators = ';,'
            """ Separators used between subparts. Each character in this string is a valid separator """
            self.split_fields = DistributorsList
            """ [list(string)] List of fields to split, usually the distributors part numbers """
            self.split_fields_expand = False
            """ When `true` the fields in `split_fields` are added to the internal names """
            self.use_ref_sep_for_first = True
            """ Force the reference separator use even for the first component in the list (KiCost behavior) """
            self.value_alt_field = 'value_subparts'
            """ Field containing replacements for the `Value` field. So we get real values for split parts """

    def config(self, parent):
        super().config(parent)
        if not self.separators:
            self.separators = ';,'
        if not self.mult_separators:
            self.mult_separators = ':'
        if not self.ref_sep:
            self.ref_sep = '#'
        if isinstance(self.split_fields, type):
            self.split_fields = DISTRIBUTORS_F
        else:
            if self.split_fields_expand:
                self.split_fields.extend(DISTRIBUTORS_F)
        # (?<!\\) is used to skip \;
        self._part_sep = re.compile(r'(?<!\\)\s*['+self.separators+r']\s*')
        self._qty_sep = re.compile(r'(?<!\\)\s*['+self.mult_separators+r']\s*')
        # TODO: The spaces here seems a bug
        self._esc = re.compile(r'\\\s*(['+self.separators+self.mult_separators+r'])\s*')
        self._num_format = re.compile(r"^\s*[\-\+]?\s*[0-9]*\s*[\.\/]*\s*?[0-9]*\s*$")
        self._remove_sep = re.compile(r'[\.\/]')
        # The list of all fields that controls the process
        self._fields = self.split_fields
        if self.manf_pn_field:
            self._fields.append(self.manf_pn_field)
        # List of fields that needs qty computation
        if isinstance(self.check_multiplier, type) or self.check_multiplier is None:
            self.check_multiplier = self._fields
        self.check_multiplier = set(self.check_multiplier)

    def subpart_list(self, value):
        """ Split a field containing self.separators into a list """
        return self._part_sep.split(value.strip())

    def manf_code_qtypart(self, value):
        # Remove any escape backslashes preceding PART_SEPRTR.
        value = self._esc.sub(r'\1', value)
        strings = self._qty_sep.split(value)
        if len(strings) == 2:
            # Search for numbers, matching with simple, frac and decimal ones.
            string0_test = re.match(self._num_format, strings[0])
            string1_test = re.match(self._num_format, strings[1])
            if string0_test and not(string1_test):
                qty = strings[0].strip()
                part = strings[1].strip()
            elif not(string0_test) and string1_test:
                qty = strings[1].strip()
                part = strings[0].strip()
            elif string0_test and string1_test:
                # May be just a numeric manufacturer/distributor part number,
                # in this case, the quantity is the shortest string not
                # considering "." and "/" marks.
                if len(self._remove_sep.sub('', strings[0])) < len(self._remove_sep.sub('', strings[1])):
                    qty = strings[0].strip()
                    part = strings[1].strip()
                else:
                    qty = strings[1].strip()
                    part = strings[0].strip()
            else:
                qty = '1'
                part = strings[0].strip() + strings[1].strip()
            if qty == '':
                qty = '1'
        else:
            qty = '1'
            part = ''.join(strings)
        if GS.debug_level > 2 and qty != '1':
            logger.debug('Subparts filter: `{}` -> part `{}` qty `{}`'.format(value, part, qty))
        return qty, part

    @staticmethod
    def qty_to_float(qty):
        try:
            if '/' in qty:
                vals = qty.split('/')
                return float(vals[0])/float(vals[1])
            return float(qty)
        except ValueError:
            logger.error('Internal error qty_to_float("{}"), please report'.format(qty))

    def do_split(self, comp, max_num_subparts, split_fields):
        """ Split `comp` according to the detected subparts """
        # Split it
        multi_part = max_num_subparts > 1
        if multi_part and GS.debug_level > 1:
            logger.debug("Splitting {} in {} subparts".format(comp.ref, max_num_subparts))
        split = []
        # Compute the total for the modified value
        total_parts = max_num_subparts if self.modify_first_value else max_num_subparts-1
        # Check if we have replacements for the `Value` field
        alt_values = []
        alt_v = comp.get_field_value(self.value_alt_field)
        if alt_v:
            alt_values = self.subpart_list(alt_v)
        alt_values_len = len(alt_values)
        for i in range(max_num_subparts):
            new_comp = deepcopy(comp)
            if multi_part:
                # Adjust the reference name
                if self.use_ref_sep_for_first:
                    new_comp.ref = new_comp.ref+self.ref_sep+str(i+1)
                elif i > 0:
                    # I like it better. The first is usually the real component, the rest are accessories.
                    new_comp.ref = new_comp.ref+self.ref_sep+str(i)
                # Adjust the suffix to be "sort friendly"
                # Currently useless, but could help in the future
                new_comp.ref_suffix = str(int(new_comp.ref_suffix)*100+i)
                # Adjust the value field
                if i < alt_values_len:
                    # We have a replacement
                    new_comp.set_field('value', alt_values[i])
                elif self.modify_value:
                    idx = i
                    if self.modify_first_value:
                        idx += 1
                    if self.modify_first_value or i:
                        new_comp.set_field('value', new_comp.value+' - p{}/{}'.format(idx, total_parts))
            # Adjust the related fields
            prev_qty = None
            prev_field = None
            max_qty = 0
            if not self.check_multiplier.intersection(split_fields):
                # No field to check for qty here, default to 1
                max_qty = 1
            for field, values in split_fields.items():
                check_multiplier = field in self.check_multiplier
                value = ''
                qty = '1'
                if len(values) > i:
                    value = values[i]
                    if check_multiplier:
                        # Analyze the multiplier
                        qty, value = self.manf_code_qtypart(value)
                        if prev_qty is not None and qty != prev_qty and field != self.manf_field:
                            logger.warning(W_PARTMULT+'Different part multiplier on {r}, '
                                           'field {c} has {cn} and {lc} has {lcn}.'
                                           .format(r=new_comp.ref, c=prev_field, cn=prev_qty, lc=field, lcn=qty))
                        prev_qty = qty
                        prev_field = field
                new_comp.set_field(field, value)
                if check_multiplier:
                    new_comp.set_field(field+'_qty', qty)
                    max_qty = max(max_qty, self.qty_to_float(qty))
            new_comp.qty = max_qty
            split.append(new_comp)
        if not multi_part and int(max_qty) == 1:
            # No real split and no multiplier
            return
        if GS.debug_level > 2:
            logger.debug('Old component: '+comp.ref+' '+str([str(f) for f in comp.fields]))
            logger.debug('Fields to split: '+str(split_fields))
            logger.debug('New components:')
            for c in split:
                logger.debug(' '+c.ref+' '+str([str(f) for f in c.fields]))
        return split

    def filter(self, comp):
        """ Look for fields containing `part1; mult:part2; etc.` """
        # Analyze how to split this component
        max_num_subparts = 0
        split_fields = {}
        field_max = None
        for field in self._fields:
            value = comp.get_field_value(field)
            if not value:
                # Skip it if not used
                continue
            subparts = self.subpart_list(value)
            split_fields[field] = subparts
            num_subparts = len(subparts)
            if num_subparts > max_num_subparts:
                field_max = field
                max_num_subparts = num_subparts
            # Print a warning if this field has a different amount
            if num_subparts != max_num_subparts:
                logger.warning(W_NUMSUBPARTS+'Different subparts amount on {r}, field {c} has {cn} and {lc} has {lcn}.'
                               .format(r=comp.ref, c=field_max, cn=max_num_subparts, lc=field, lcn=num_subparts))
        if len(split_fields) == 0:
            # Nothing to split
            return
        # Split the manufacturer name
        # It can contain just one name, so we exclude it from the above warning
        if self.manf_field:
            value = comp.get_field_value(self.manf_field)
            if value:
                manfs = self.subpart_list(value)
                if len(manfs) == 1:
                    # If just one `manf` apply it to all
                    manfs = [manfs[0]]*max_num_subparts
                else:
                    # Expand the "repeat" indicator
                    for i in range(len(manfs)-1):
                        if manfs[i+1] == '~':
                            manfs[i+1] = manfs[i]
                split_fields[self.manf_field] = manfs
        # Now do the work
        return self.do_split(comp, max_num_subparts, split_fields)
