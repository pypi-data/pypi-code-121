from price_val_engine.core.validations.base_rules import BaseRule


class DeltaPercentageFromLastDayRule(BaseRule):
    name = "revised-vs-listing-price-delta"
    # REPIVISED VS LISTING PRICE DELTA
    severity = None
    message = "Revised Vs Listing price delta greater than +-5% from Last Day. Actual is {1}%"
    
    def is_valid(self, item, target_field="final_liquidation_price"):
        final_lp = float(item['final_liquidation_price'])
        lp = float(item['lp'])
        
        delta = final_lp - lp
        delta_pct = round(100 * delta / (lp or 0.000001) ,0)
        
        if  -5 <= delta_pct  <= 5:
            return True
        
        elif  -7 <= delta_pct  <= 7:
            self.severity = 'LOW'
            self.message= self.message.format("7%", delta_pct) 
            return False
        
        elif  -10 <= delta_pct  <= 10:
            self.severity = 'MEDIUM'
            self.message = self.message.format("10%", delta_pct) 
            return False
        
        else:
            self.severity = 'HIGH'
            self.message= "Revised Vs Listing price delta more than 10%. Actual is {}%".format(delta_pct) 
            return False    