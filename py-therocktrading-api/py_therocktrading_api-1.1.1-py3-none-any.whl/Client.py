from TheRockTrading.Config import Config 

class Client(Config):
    def __init__(self, API='', API_SECRET='', staging=False):
        self.configuration(API, API_SECRET, staging)


    def balance(self, fund_id):
        """
        Get your balance in a specific currency.
           
        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/balances/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def balances(self):
        """
        Get a list of all your balances in any currency.
        """
        self.url_creator('/balances')
        response = self.requests_and_parse('GET')
        return response


    def currencies_adresses(self, fund_id):
        """
        Get user's addresses per currency.
        
        Parameters Mandatory:
        - fund_id -> string: fund symbol

        Parameters Optional:
        - direction -> String: filter addresses by direction. Accepted values are 'deposit' or 'withdraw'
        - network -> String: filter addresses by network. Accepted values are 'bitcoin', 'litecoin', ...
        - bech32 -> Booelan: filter addresses to get bech32 addresses only. 
                             Option accepted combined with 'BTC' currency only
        - transparent -> Boolean: filter addresses to get transparent addresses only. 
                                  Option accepted combined with 'ZEC' currency only
        - private -> Boolean: filter addresses to get private addresses only. 
                              Option accepted combined with 'ZEC' currency only
        - unused -> Boolean: filter addresses in order to get yet used addresses. 
                             Option accepted combined with 'deposit' direction only
        - per_page -> Integer: number of addresses per page. default 25 max 200
        - page -> Integer: page number. default 1
        """
        self.url_creator(f'/currencies/{fund_id}/addresses')
        response = self.requests_and_parse('GET')
        return response


    def new_deposit_address(self):
        """
        Submit a new address generation request for a currency. 
        A new address request returns no data if succeeds.

        Parameters Mandatory:
        - fund_id -> string: fund symbol

        Parameters Optional:
        - network -> String: Network on which you are requesting a new address. 
                             Accepted values are 'bitcoin', 'litecoin', ...
        - segwit -> Boolean: Set to true in order to request a segwit address generation [default]. 
                             Parameter accepted when combined with BTC currency only.
        - bech32 -> Booelan: Set to true in order to request a bech32 address generation.
                             Option accepted combined with 'BTC' currency only
        - transparent -> Boolean: Set to true in order to request a transparent address generation [default].
                                  Option accepted combined with 'ZEC' currency only
        - private -> Boolean: Set to true in order to request a private address generation.
                              Option accepted combined with 'ZEC' currency only
        - confidential ->  Boolean: Set to true in order to request a confidential address generation. 
                                    Parameter accepted when combined with BTC currency and 'liquid' network only.
        """
        self.url_creator(f'/currencies/{fund_id}/addresses')
        response = self.requests_and_parse('POST')
        return response


    def transaction(self, transaction_id):
        """
        Show your transaction by ID.

        Parameters Mandatory:
        - transaction_id -> Integer: transaction id
        """
        self.url_creator(f'/transactions/{transaction_id}')
        response = self.requests_and_parse('GET')
        return response


    def transactions(self):
        """
        Get user's transactions

        Parameters Optional:
        - page -> Integer: page number. default 1
        - fund_id -> String: filter transactions by fund symbol
        - currency -> String: filter transactions by currency
        - after -> String: filter transactions after a certain timestamp 
                           (format %Y-%m-%dT%H:%M:%S%Z ex. 2015-02-06T08:47:26Z )
        - before -> String: filter transactions before a certain timestamp 
                            (format %Y-%m-%dT%H:%M:%S%Z )
        - type -> String: filter transactions by transaction type
        - order_id -> String: filter transactions by a specific order ID
        - trade_id -> String: filter transactions by a specific trade ID
        - transfer_method -> String: filter transactions by transfer method. 
                                     Accepted methods are: wire_transfer, ripple, 
                                     greenaddress, bitcoin, litecoin, namecoin, 
                                     peercoin, dogecoin
        - transfer_recipient -> String: filter transactions by a specific recipient 
                                        (e.g. Bitcoin address, IBAN)
        - transfer_id ->  String: filter transactions by a specific transfer ID 
                                  (e.g. Bitcoin TX hash)
        """
        self.url_creator(f'/transactions')
        response = self.requests_and_parse('GET')
        return response


    def discount(self, fund_id):
        """
        Returns currency related discount

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/discounts/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def discounts(self):
        """
        Returns currencies related discount
        """
        self.url_creator('/discounts')
        response = self.requests_and_parse('GET')
        return response


    def withdraw_limit(self, fund_id):
        """
        Will return a currency related withdraw limit

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/withdraw_limits/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def withdraw_limits(self):
        """
        Will return a list of your global and currently available withdraw levels.
        """
        self.url_creator(f'/withdraw_limits')
        response = self.requests_and_parse('GET')
        return response


    def withdraw(self):
        """
        Will return a list of your global and currently available withdraw levels.

        Parameters Mandatory:
        - currency -> String: Currency you want to withdraw
        - amount -> Float: Withdrawal amount
        - destination_address -> String: Destination address

        Parameters Optional:
        - withdraw_method -> String: The withdraw method to be used. 
                                     A default method will be applied if not specified. 
                                     Alternative withdrawal methods accepted are 'RIPPLE', 'LIQUID', 'LIGHTNING'
        - withdraw_priority -> String: Options are 'regular' (default), 'high'. 
                                       Regular priority withdrawals are grouped and executed within 15 minutes. 
                                       High priority withdrawals are executed immediately. 
                                       Check on therocktrading.com page how fees are respectively applied. 
                                       Currently available for bitcoin withdrawals only.
        - destination_tag -> Integer: Destination tag useful when combined with RIPPLE withdrawal method


        """
        self.url_creator(f'/atms/withdraw')
        response = self.requests_and_parse('POST')
        return response


    def close_at_market(self, fund_id, order_id):
        """
        Close all open positions originated by a specific order ID
           
        Parameters Mandatory:
        - fund_id -> string: fund symbol
        - order_id -> String: order ID
        """
        self.url_creator(f'/funds/{fund_id}/main_positions/{order_id}')
        response = self.requests_and_parse('DELETE')
        return response


    def positions_list(self, fund_id, **params):
        """
        List your margin positions grouped by originating order ID (opening order).

        Parameters Mandatory:
        - fund_id -> string: fund symbol

        Parameters Optional:
        - status -> String: filter main positions by status. Accepted values are: open, closed
        - type -> String: filter main positions by type. Accepted values are: short, long
        - page -> Integer: page number. default 1
        """
        self.url_creator(f'/funds/{fund_id}/main_positions?', params=params)
        response = self.requests_and_parse('GET')
        return response


    def positions_show(self, fund_id, order_id):
        """
        Show specific main position.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        - order_id -> String: order ID
        """
        self.url_creator(f'/funds/{fund_id}/main_positions/{order_id}')
        response = self.requests_and_parse('GET')
        return response


    def transfer_balance(self, fund_id, order_id, **params):
        """
        Transfer the amount of base currency required by maintenance_balance 
        (See showMainPosition API doc for further infomation ) to close a position. 
        It applies only to short positions when the amount of base currency is not sufficient to close them.

        Parameters Mandatory:
        - amount -> String: the amount you want to transfer
        - currency -> String: base currency operating on the fund. (e.g. fund: BTCEUR -> base_currency: EUR)
        """
        self.url_creator(f'/funds/{fund_id}/main_positions/{order_id}/transfer_balance?', params=params)
        response = self.requests_and_parse('POST')
        return response


    def position_balances(self, fund_id):
        """
        An overall view of margin trading personal balances, both base and trade currency, for each fund/currency pairs. 
        Position balance is part of the regular user balances, but it is related to margin trading. 
        For example, you have to refer to position balance in order to see if and how you can close a position. 
        This api will return the sum of all your positions balances.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/funds/{fund_id}/position_balances')
        response = self.requests_and_parse('GET')
        return response


    def positions(self, fund_id, **params):
        """
        List your margin positions.

        Parameters Optional:
        - status -> String: filter positions by status. Accepted values are: open, closed
        - type -> String: filter positions by type. Accepted values are: short, long
        - page -> Integer: page number. default 1
        """
        self.url_creator(f'/funds/{fund_id}/positions?', params=params)
        response = self.requests_and_parse('GET')
        return response


    def position_show(self, fund_id, order_id):
        """
        Show specific position.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        - order_id -> String: order ID
        """
        self.url_creator(f'/funds/{fund_id}/positions/{order_id}')
        response = self.requests_and_parse('GET')
        return response
        

    def currencies(self):
        """
        Get all currencies info.
        """
        self.url_creator('/currencies')
        response = self.requests_and_parse('GET')
        return response


    def currency(self, fund_id):
        """
        Get single currency info

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/currencies/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def fair_value(self, fund_id):
        """
        Get all fair values by currency

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/fair_values/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def fair_value(self):
        """
        Get all fair values.
        """
        self.url_creator(f'/fair_values')
        response = self.requests_and_parse('GET')
        return response


    def fund(self, fund_id):
        """
        Get single fund data.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/funds/{fund_id}')
        response = self.requests_and_parse('GET')
        return response


    def funds(self):
        """
        Get all funds at once.
        """
        self.url_creator(f'/funds')
        response = self.requests_and_parse('GET')
        return response


    def ohlc_statistics(self, fund_id, **params):
        """
        Get Open-high-low-close chart statistics.

        Parameters Mandatory:
        - fund_id -> String: fund symbol

        Parameters Optional:
        - period -> String: Sampling period in minutes. Default: 15, Min: 5
        - before -> Date: Get only trades executed before a certain timestamp ( format %Y-%m-%dT%H:%M:%S%Z ). 
                    Must be a multiple of 'period' minutes. Default: now().
        - after -> Date: Get only trades executed after a certain timestamp ( format %Y-%m-%dT%H:%M:%S%Z). 
                   Must be a multiple of 'period' minutes. Default is one day behind "before"
        - sort -> String: Accepted values are: ASC|DESC. Default: DESC
        """
        self.url_creator(f'/funds/{fund_id}/ohlc_statistics?', params=params)
        response = self.requests_and_parse('GET')
        return response


    def orderbook(self, fund_id, **params):
        """
        The orderbook api will provide the entire/partial set of bids and asks for a specific currency pair (fund).

        Parameters Mandatory:
        - fund_id -> string: fund symbol

        Parameters Optional:
        - limit -> Integer: max number of entries to return for each side (asks and bids)
        - currency_for_depth -> String: currency on which to apply a depth filter
        - depth -> String: generic depth filter to apply to both asks and bids
        - ask_depth -> String: ask depth filter to apply to asks entries only 
                               (generic depth param will be applied if not specified)
        - bid_depth -> String: bid depth filter to apply to bids entries only
                               (generic depth param will be applied if not specified)
        """
        self.url_creator(f'/funds/{fund_id}/orderbook', params=params)
        response = self.requests_and_parse('GET')
        return response


    def ticker(self, fund_id):
        """
        Get ticker of a choosen fund.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/funds/{fund_id}/ticker/')
        response = self.requests_and_parse('GET')
        return response


    def tickers(self):
        """
        Get all tickers at once.
        """
        self.url_creator('/funds/tickers')
        response = self.requests_and_parse('GET')
        return response


    def trades(self, fund_id, **params):
        """
        Get all trades.

        Parameters Mandatory:
        - fund_id -> string: fund symbol

        Parameters Optional:
        - trade_id -> Integer: get all trades starting from a specific trade_id
        - per_page -> Integer: number of trades per page. default 25 max 200
        - page -> Integer: page number. default 1
        - after -> String: get only trades executed after a certain timestamp 
                           (format %Y-%m-%dT%H:%M:%S%Z ex. 2015-02-06T08:47:26Z)
        - before -> String: get only trades executed before a certain timestamp
                            (format %Y-%m-%dT%H:%M:%S%Z )
        - order -> String: order trades by id. Accepted values are: ASC|DESC. Default: DESC
        """
        self.url_creator(f'/funds/{fund_id}/trades?', params=params)
        response = self.requests_and_parse('GET')
        return response



    def cancel_all_orders(self, fund_id, order_id):
        """
        Remove all active orders from the specified market.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        """
        self.url_creator(f'/funds/{fund_id}/orders/remove_all')
        response = self.requests_and_parse('DELETE')
        return response


    def cancel_order(self, fund_id):
        """
        Remove an active order from the specified market.

        Parameters Mandatory:
        - fund_id -> string: fund symbol
        - order_id -> string: the id of the order to be cancelled.
        """
        self.url_creator(f'/funds/{fund_id}/orders/{order_id}')
        response = self.requests_and_parse('DELETE')
        return response


    def orders(self, fund_id, **params):
        """
        List your orders per fund_id. All active or conditional orders are returned by default.

        Parameters Mandatory:
        - fund_id -> String: fund symbol
        - side -> String: "buy" or "sell" order. "close_long" or "close_short" to place a closing position order 
                        (position_id or position_order_id parameter required).
        - amount -> String: the amount you want to Buy/Sell
        - price -> String: the price of your order to be filled. If price is 0 (zero) a market order will be placed.
        
        Parameters Optional:
        - after -> String: filter orders after a certain timestamp 
                             (format %Y-%m-%dT%H:%M:%S%Z ex. 2015-02-06T08:47:26Z)
        - before -> String: filter orders before a certain timestamp 
                              (format %Y-%m-%dT%H:%M:%S%Z )
        - status -> String: filter orders by status. Accepted values are: active, conditional, executed and deleted
        - side -> String: filter orders by side. Accepted values are: buy, sell
        - position_id -> Integer: filter orders by margin position ID. It collects all closing orders related to a specific margin position ID
        """
        self.url_creator(f'/funds/{fund_id}/orders', params=params)
        response = self.requests_and_parse('GET')
        return response    


    def place_order(self, fund_id, **params):
        """
        Place an order on the specified market, at specified conditions.

        Parameters Mandatory:
        - fund_id -> String: fund symbol
        - side -> String: "buy" or "sell" order. "close_long" or "close_short" to place a closing position order 
                        (position_id or position_order_id parameter required).
        - amount -> String: the amount you want to Buy/Sell
        - price -> String: the price of your order to be filled. If price is 0 (zero) a market order will be placed.
        
        Parameters Optional:
        - conditional_type -> String: specify a conditional type in order to place a conditional order. 
                                      Accepted values are [stop_loss|take_profit]
        - conditional_price -> String: conditional price represent the price at which your order will be triggered. 
                                       Need to be specified when conditional_type param is present.
        - leverage -> String: leverage to apply on "buy" or "sell" orders only. 
                                       Leverage values are configured per fund. See fund API doc for further infomation.
        - position_id -> String: position_id along with "close_long" or "close_short" parameter in order to close a single position.
        - position_order_id -> String: position_order_id along with "close_long" or "close_short" as an alternative to position_id parameter
                                       in order to close all open positions originated by the same leveraged order.
        """
        self.url_creator(f'/funds/{fund_id}/orders?', params=params)
        response = self.requests_and_parse('POST')
        return response


    def show_order(self, fund_id, order_id):
        """
        Show your order by ID.

        Parameters Mandatory:
        - fund_id -> String: fund symbol
        - order_id -> String: order ID
        """
        self.url_creator(f'/funds/{fund_id}/orders/{order_id}')
        response = self.requests_and_parse('GET')
        return response    


    def user_trades(self, fund_id, order_id, **params):
        """
        Show your order by ID.

        Parameters Mandatory:
        - fund_id -> String: fund symbol

        Parameters Optional:
        - trade_id -> Integer: get all trades starting from a specific trade_id
        - page -> Integer: page number. default 1
        - per_page -> Integer: number of trades per page. default 25 max 200
        - after -> String: get only trades executed after a certain timestamp 
                           (format %Y-%m-%dT%H:%M:%S%Z ex. 2015-02-06T08:47:26Z)
        - before -> String: get only trades executed before a certain timestamp 
                            (format %Y-%m-%dT%H:%M:%S%Z)
        """
        self.url_creator(f'/funds/{fund_id}/trades', params=params)
        response = self.requests_and_parse('GET')
        return response