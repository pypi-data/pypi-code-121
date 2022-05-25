
class ObjEvmToken:
    token_address = None
    abi = None
    chain_id = None 
    symbol = None
    name = None
    decimals = None
    token_class = None
    totalsupply = None
    keywords = None
    telegram_link = None
    creator_address = None
    creation_timestamp = None 
    creation_block_number = None 
    creation_tx_hash = None
    
    liquidity_pool_address = ''
    initialPrice = 0
    buy_gas_used_hp_check = 0 
    sell_gas_used_hp_check = 0 
    max_fee_per_gas = 100000000000
    max_prio_fee_per_gas = 3000000000
    gas_price = 100000000000
    slippage_percent = 50
    tax_buy_limit = 15
    tax_sell_limit = 60
    is_active = 'Y'
    is_completed = 'N'
    buy_with_hp_check = 'Y'
    created_at = 0
    modified_at = 0
    user_number = 0
    delayed_hp_protection = 'Y'
    automatic_profit_trading = 'Y'


    def __init__(self):
        self.db_id = 0

    def __eq__(self, other): 
        if not isinstance(other, ObjEvmToken):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return (self.db_id == other.db_id and 
                self.txHash == other.txHash and
                self.network == other.network and
                self.chain_id == other.chain_id and
                self.tokenAddr == other.tokenAddr and
                self.liquidity_pool_address == other.liquidity_pool_address and
                self.amountBuy == other.amountBuy and
                self.amountToken == other.amountToken and
                self.token_symbol == other.token_symbol and
                self.profitTaken == other.profitTaken and
                self.initialPrice == other.initialPrice and
                self.buy_gas_used_hp_check == other.buy_gas_used_hp_check and
                self.sell_gas_used_hp_check == other.sell_gas_used_hp_check and
                self.max_fee_per_gas == other.max_fee_per_gas and
                self.max_prio_fee_per_gas == other.max_prio_fee_per_gas and
                self.gas_price == other.gas_price and
                self.slippage_percent == other.slippage_percent and
                self.tax_buy_limit == other.tax_buy_limit and
                self.tax_sell_limit == other.tax_sell_limit and
                self.is_active == other.is_active and
                self.is_completed == other.is_completed and
                self.buy_with_hp_check == other.buy_with_hp_check and
                self.created_at == other.created_at and
                self.modified_at == other.modified_at and
                self.user_number == other.user_number and
                self.delayed_hp_protection == other.delayed_hp_protection and
                self.automatic_profit_trading == other.automatic_profit_trading)

    def clone(self):
        retTok = ObjEvmToken()
        retTok.db_id = self.db_id
        retTok.txHash = self.txHash
        retTok.network = self.network
        retTok.chain_id = self.chain_id
        retTok.tokenAddr = self.tokenAddr
        retTok.liquidity_pool_address = self.liquidity_pool_address
        retTok.amountBuy = self.amountBuy
        retTok.amountToken = self.amountToken
        retTok.token_symbol = self.token_symbol
        retTok.profitTaken = self.profitTaken
        retTok.initialPrice = self.initialPrice
        retTok.buy_gas_used_hp_check = self.buy_gas_used_hp_check
        retTok.sell_gas_used_hp_check = self.sell_gas_used_hp_check
        retTok.max_fee_per_gas = self.max_fee_per_gas
        retTok.max_prio_fee_per_gas = self.max_prio_fee_per_gas
        retTok.gas_price = self.gas_price
        retTok.slippage_percent = self.slippage_percent
        retTok.tax_buy_limit = self.tax_buy_limit
        retTok.tax_sell_limit = self.tax_sell_limit
        retTok.is_active = self.is_active
        retTok.is_completed = self.is_completed
        retTok.buy_with_hp_check = self.buy_with_hp_check
        retTok.created_at = self.created_at
        retTok.modified_at = self.modified_at
        retTok.user_number = self.user_number
        retTok.delayed_hp_protection = self.delayed_hp_protection
        retTok.automatic_profit_trading = self.automatic_profit_trading
        return retTok