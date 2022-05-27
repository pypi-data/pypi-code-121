class Pool(object):

    def __init__(
        self,
        main,
    ):
        self.main = main

    # -----------------------------------------------------------
    # Transactions
    # -----------------------------------------------------------

    def update_router_permissions(
        self,
        pool,
        router,
        permissions,
        options=None
    ):
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool),
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateRouterPermissions(
                router, permissions
            ),
            options=options
        )

    def update_signer(
        self,
        signer,
        options=None
    ):

        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool),
        )

        return self.main.send_eth_transaction(
            method=contract.functions.updateSigner(
                self.main.web3.toChecksumAddress(signer),
            ),
            options=options
        )

    def update_lp_account(
        self,
        pool,
        whitelist,
        status,
        options=None
    ):
        '''
        Pool owners can authorize/unauthorize whitelist addresses that can 
        contribute assets to the pool. 
        '''

        checksum_whitelist = []
        for lp_account in whitelist:
            checksum_whitelist.append(
                self.main.web3.toChecksumAddress(lp_account))

        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateLpAccount(
                checksum_whitelist, status
            ),
            options=options
        )

    def update_migration_pool(
        self,
        current_pool,
        margin_pool,
        options=None
    ):

        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(current_pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateMigrationPool(migration_pool),
            options=options
        )

    def update_migrate_mode(
        self,
        pool,
        migrate_mode,
        options=None
    ):

        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateMigrateMode(migrateMode),
            options=options
        )

    def update_hedging_account(
        self,
        pool,
        whitelist,
        status,
        options=None
    ):
        '''
        Pool owners can authorize/unauthorize whitelist addresses that be used to withdraw
        funds
        '''

        checksum_whitelist = []
        for hedging_account in whitelist:
            checksum_whitelist.append(
                self.main.web3.toChecksumAddress(hedging_account))

        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateHedgingAccount(
                checksum_whitelist, status
            ),
            options=options
        )

    def list_asset(
        self,
        pool,
        token,
        cap,
        options=None
    ):
        '''
        List a new asset.
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.listAsset(token, cap),
            options=options
        )

    def update_cap(
        self,
        pool,
        token,
        cap,
        options=None
    ):
        '''
        Update an asset's cap.
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateCap(token, cap),
            options=options
        )

    def stop_trading(
        self,
        pool,
        stop,
        options=None
    ):

        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateTrading(stop),
            options=options
        )

    def update_fees(
        self,
        pool,
        fees,
        options=None
    ):

        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.updateFees(fees),
            options=options
        )

    def transfer_assets(
        self,
        pool,
        token,
        recipient,
        amount,
        options=None
    ):
        '''
        Transfer postive equity balance to CeFi venue to rebalance pools. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )
        return self.main.send_eth_transaction(
            method=contract.functions.transferAssets(
                self.main.web3.toChecksumAddress(token),
                self.main.web3.toChecksumAddress(recipient),
                amount
            ),
            options=options
        )

    def get_pool_name(
        self,
        pool,
    ):
        '''
        Query pool name. Pool's name is the same as Lp token name. 
        '''
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getPoolName().call()
        return result

    def get_signer(
        self,
        pool,
    ):
        '''
        Query signer address.
        '''
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getSigner().call()
        return result

    def get_reserves(
        self,
        pool,
        token,
    ):
        '''
        Query pool's reserves for an asset.
        For eth, set token address to ZERO_ADDRESS
        '''
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getReserves(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_hToken(
        self,
        pool,
        token,
    ):
        '''
        Query a token's hToken address associated with the pool. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getHToken(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_withdraw_limit(
        self,
        pool,
        token,
    ):
        '''
        Query an account's withdraw limit. W.L is updated each week. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getWithdrawLimit(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_cap(
        self,
        pool,
        token,
    ):
        '''
        Query a public pools max capacity for an asset. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getCap(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def asset_listed(
        self,
        pool,
        token,
    ):
        '''
        Check if asset is listed. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.assetListed(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_net_payout(
        self,
        pool,
        token,
    ):
        '''
        Query pool's total payout. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getNetPayout(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_withdrawal_timestamp(
        self,
        pool,
        token,
    ):
        '''
        Query pool's total payout. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getWithdrawalTimestamp(
            self.main.web3.toChecksumAddress(token)
        ).call()
        return result

    def get_payout(
        self,
        pool,
        token,
        liquidity_provider,
    ):
        '''
        Query a liquidity provider's total payout. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.computeLpPayout(
            self.main.web3.toChecksumAddress(token),
            self.main.web3.toChecksumAddress(liquidity_provider)
        ).call()
        return result

    def get_nonce(
        self,
        pool,
        account,
    ):
        '''
        Query nonce associated with an account.
        '''
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getNonce(
            self.main.web3.toChecksumAddress(account)
        ).call()
        return result

    def get_migration_pool(
        self,
        pool,
    ):
        '''
        Query migration pool address. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getMigrationPool().call()
        return result

    def get_migration_mode(
        self,
        pool,
    ):
        '''
        Check if pool is in migration mode. 
        '''
        contract = self.main.create_contract(
            'IHashflowSpotPubPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getMigrationMode().call()
        return result

    def get_governance(
        self,
        pool,
    ):
        '''
        Query governance contract address. 
        '''
        contract = self.main.create_contract(
            'IHashflowPool',
            self.main.web3.toChecksumAddress(pool)
        )

        result = contract.functions.getGovernance().call()
        return result
