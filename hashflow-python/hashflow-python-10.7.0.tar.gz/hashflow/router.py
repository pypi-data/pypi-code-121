from hashflow.constants import ZERO_ADDRESS
from hashflow.util import Trade, Flag


class Router(object):

    def __init__(
        self,
        main,
    ):
        self.main = main

        # initialize contracts
        self.router = self.main.create_hashflow_contract(
            'HashflowRouter',
            self.main.network_id
        )

    def add_liquidity_private_pool(
        self,
        pool,
        token,
        amount,
        options=None,
    ):
        '''
        Add liquidity into private pool.
        '''

        if token == ZERO_ADDRESS:
            if options is None:
                options = dict(
                    value=amount
                )
            else:
                options['value'] = amount

        return self.main.send_eth_transaction(
            method=self.router.functions.addLiquidityPrivatePool(
                self.main.web3.toChecksumAddress(pool),
                self.main.web3.toChecksumAddress(token),
                amount,
            ),
            options=options
        )

    def add_liquidity_public_pool(
        self,
        pool,
        token,
        amount,
        options=None,
    ):
        '''
        Add liquidity into public pool.
        '''

        if token == ZERO_ADDRESS:
            if options is None:
                options = dict(
                    value=amount
                )
            else:
                options['value'] = amount

        return self.main.send_eth_transaction(
            method=self.router.functions.addLiquidityPublicPool(
                self.main.web3.toChecksumAddress(pool),
                self.main.web3.toChecksumAddress(token),
                amount,
            ),
            options=options
        )

    def remove_liquidity_private_pool(
        self,
        pool,
        token,
        amount,
        recipient=ZERO_ADDRESS,
        options=None,
    ):
        '''
        Remove liquidity from the private pool.
        '''
        _recipient = ZERO_ADDRESS
        if recipient != ZERO_ADDRESS:
            _recipient = recipient

        contract = self.main.create_contract(
            'IHashflowPrivPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.withdraw(
                self.main.web3.toChecksumAddress(token),
                self.main.web3.toChecksumAddress(_recipient),
                amount,
            ),
            options=options,
        )

    def remove_liquidity_public_pool(
        self,
        pool,
        token,
        burn_amount,
        options=None,
    ):
        '''
        Remove liquidity from public pool.
        '''

        return self.main.send_eth_transaction(
            method=self.router.functions.removeLiquidityPublicPool(
                self.main.web3.toChecksumAddress(pool),
                self.main.web3.toChecksumAddress(token),
                burn_amount,
            ),
            options=options,
        )

    def trade_single_hop(
        self,
        quote_data,
        signed_quote,
        effective_base_token_amount=None,
        options=None,
    ):

        if effective_base_token_amount is None:
            effective_base_token_amount = quote_data.base_token_amount

        if quote_data.base_token_address == ZERO_ADDRESS:
            if options is None:
                options = dict(
                    value=(effective_base_token_amount)
                )
            else:
                options['value'] = (
                    effective_base_token_amount
                )

        if quote_data.flag == Flag.off:
            self.k_value_or_nonce = quote_data.k_value
        if quote_data.flag == Flag.on:
            self.k_value_or_nonce = quote_data.k_value
        if quote_data.flag == Flag.na:
            self.k_value_or_nonce = quote_data.nonce

        quote = {
            'pool': self.main.web3.toChecksumAddress(quote_data.pool),
            'eoa': self.main.web3.toChecksumAddress(
                        quote_data.eoa),
            'trader': self.main.web3.toChecksumAddress(
                        quote_data.trader),
            'effectiveTrader': self.main.web3.toChecksumAddress(
                        quote_data.effectiveTrader),
            'baseToken': self.main.web3.toChecksumAddress(
                    quote_data.base_token_address),
            'quoteToken': self.main.web3.toChecksumAddress(
                        quote_data.quote_token_address),
            'effectiveBaseTokenAmount': effective_base_token_amount,
            'maxBaseTokenAmount': quote_data.base_token_amount,
            'maxQuoteTokenAmount': quote_data.quote_token_amount,
            'fees': quote_data.fees,
            'quoteExpiry': quote_data.expiry,
            'kValueOrNonce': self.k_value_or_nonce,
            'tradeEOA': quote_data.trade_eoa,
            'flag': quote_data.flag,
            'txid': quote_data.txid,
            'signedQuote': signed_quote
        }

        return self.main.send_eth_transaction(
            method=self.router.functions.tradeSingleHop(quote),
            options=options
        )

    def set_weth(
        self,
        weth,
        options=None,
    ):
        '''
        Update weth address in the router.
        '''

        return self.main.send_eth_transaction(
            method=self.router.functions.setWeth(
                self.main.web3.toChecksumAddress(weth),
            ),
            options=options
        )
