from price_val_engine.core import utils
from price_val_engine.conf import settings
from price_val_engine.core.validations.base_rules import BaseRule


EMPTY_VALUES = settings.EMPTY_VALUES or (None, "", [], (), {})

class NullNegativeZeroValidationRule(BaseRule):
    name = 'null-negative-zero-rule'
    message = "Invalid Value"
    severity = 'HIGH'
    
    def is_valid(self, item, target_field="final_liquidation_price"):
        value = item[target_field]
        if value in EMPTY_VALUES:
            self.message =f"{target_field} - Null Value"
            return False
        if not utils.is_number(value):
            self.message = f"{target_field} - Number value Expected"
            return False
        if float(value) == 0.0:
            self.message = f"{target_field} - Zero Value"
            return False
        if float(value) < 0.0:
            self.message = f"{target_field} - Negative Value"
            return False
        return True

class OutOfRangeValidationRule(BaseRule):
    name = "price-out-of-range-rule"
    message = "Out of Range"
    severity = 'HIGH'
    
    min_value = settings.GEN_VAL_OUT_OF_RANGE_VALUE.get('min_value') or  100000.0
    max_value = settings.GEN_VAL_OUT_OF_RANGE_VALUE.get('max_value') or  10000000.0
    
    def is_valid(self, item, target_field="final_liquidation_price"):
        value = item[target_field]
        if not (self.min_value <= float(value) <= self.max_value):
            self.message = f"{target_field} {value} out of range. <min{self.min_value}> - <max{self.max_value}>"
            return False
        return True

