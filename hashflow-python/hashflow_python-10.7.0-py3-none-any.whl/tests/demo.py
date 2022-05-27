from hashflow.client import Client
from hashflow.constants import ZERO_ADDRESS, PRIV_POOL_CONTRACT, ETH_ADDRESS, ROUTER_CONTRACT
import hashflow.util as utils
import eth_account
import eth_keys

private_key = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80'
signer_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
node = 'http://127.0.0.1:8545'
hflow = Client(private_key, network_id=31337, node=node)

# private_key = '0x92faf84d1442867029be862d8e076f0cce38f43052c03ffdd3873aa6e6fc21cd'
# signer_private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'
# node = 'https://mainnet.infura.io/v3/fe673a7397d745348eb876fa3288d2cc'
# signer = '0x2150DD462B496bd5e4A37b5411c13319427BE83E'
# admin = '0x2150DD462B496bd5e4A37b5411c13319427BE83E'

#hflow = Client(private_key, network_id=1, node=node)
name = 'hashflow-7'
symbol = 'NaN'
admin = '0x70997970c51812dc3a010c7d01b50e0d17dc79c8'
signer = '0x70997970c51812dc3a010c7d01b50e0d17dc79c8'
operations = '0xf39fd6e51aad88f6f4ce6ab8827279cfffb92266'
pool = '0x710DD0333d849b46CD4ed9822d6e4a6aE6A9a99f'
eth = ZERO_ADDRESS
liquidity_provider = operations
amount = 500
txid = '0xea513029cdd1d30170053424aa835575d410d8fe6b1f2c4ac17725349c9c9b0c'
expiry = hflow.main.set_expiry(20)
flag = utils.Flag.on
testToken1 = '0x959922bE3CAee4b8Cd9a407cc3ac1C251C2007B1'
testToken2 = '0x3D63c50AD04DD5aE394CAB562b7691DD5de7CF6f'
effective_base_token_amount = 80
base_token_amount = 100
quote_token_amount = 5 

# result1 = hflow.main.factory.set_priv_pool_impl()
# result2 = hflow.main.factory.set_pub_pool_impl()
# result3 = hflow.main.factory.set_hToken_impl()
# print(result1, result2)

#hflow.main.factory.create_pool(name='hash222', symbol='sss', signer=signer)
#hflow.main.factory.create_pool(name='hash35', symbol = 'fgf', signer=signer, privPool = False, permissioned=False)

result4 = hflow.main.factory.get_pools(operations)
print(result4)

#hflow.main.erc20.set_maximum_hashflow_allowance(testToken1)
# result5 = hflow.main.erc20.allowance(testToken1, operations, '0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e')
# print((result5))
#hflow.main.router.add_liquidity_private_pool(result4[0], testToken1, amount)
#hflow.main.pool.list_asset(result4[2], testToken1, cap=1000)
#hflow.main.pool.list_asset(result4[2], eth, cap=1000)
#hflow.main.router.add_liquidity_public_pool(result4[2], eth, amount)
#hflow.main.router.add_liquidity_public_pool(result4[2], testToken1, amount)

# #print(result6)
#result = hflow.main.pool.update_hedging_account(result4[2], [signer], True)
#result7 = hflow.main.router.remove_liquidity_private_pool(result4[0], testToken1, 20, recipient=signer)
# #result8 = hflow.main.router.withdraw_all(result3[0], [eth, testToken1], signer)
#heth = hflow.main.pool.get_hToken(result4[2], eth)

#print(heth)
#hflow.main.erc20.set_maximum_hashflow_allowance(heth)
#hflow.main.governance.set_percent_withdrawal_limit(20)
#hflow.main.router.remove_liquidity_public_pool(result4[2], ETH_ADDRESS, burn_amount=2000)
#hflow.main.erc20.transfer(testToken1, result4[0], amount=100)
hflow.main.pool.transfer_assets(result4[2], eth, recipient=signer, amount=2)
# result9 = hflow.main.pool.reserves(result4[1], ETH_ADDRESS)
# print(result9, 58)
# result10 = hflow.main.pool.payout(result4[1], ETH_ADDRESS, liquidity_provider)
# print(result10)
# result11 = hflow.main.pool.estimate_burn_amount(result4[1], ETH_ADDRESS, 502)
# print(result11)

# # print(hflow.main.get_wallet_balance(signer, token=testToken1))
# # print(hflow.main.pool.reserves(result3[0], testToken1))
# hflow.main.pool.update_fees(result4[1], 200)
# # result = hflow.main.get_wallet_balance(liquidity_provider)
#quote1 = utils.Quote(name, 'TT1', 'ETH', result4[1], liquidity_provider, testToken1, eth, base_token_amount, max_base_token_amount, max_quote_token_amount, txid, expiry, flag, k_value=13)
# quote2 = utils.Quote(result4[1], liquidity_provider, eth, testToken1, base_token_amount, quote_token_amount, txid, expiry, flag, k_value=4)
# # # quote3 = utils.Quote(name, 'TT2', 'TT1', result1[3], liquidity_provider, testToken2, testToken1, base_token_amount, quote_token_amount, txid, expiry, flag, k_value=12)
quote = utils.Quote(pool=result4[2], eoa=ZERO_ADDRESS, trader=operations, effectiveTrader=operations, base_token_address=eth, quote_token_address=testToken1, base_token_amount=10, quote_token_amount=50, fees=0, expiry=expiry, flag=flag, txid=txid, k_value=4, trade_eoa=False)
# # #quote = utils.Quote(pool_name, base_token_name, quote_token_name, pool, trader, base_token_address, quote_token_address, base_token_amount, quote_token_amount, txid, expiry, flag, k_value)
# result = hflow.main.pool.reserves(result4[1], testToken1)
#print(quote)
quote_digest = hflow.main.hash_quote(quote)
#print(quote.__dict__)
signed_quote = utils.sign_digest(quote_digest, signer_private_key)
#print(signed_quote)

#hflow.main.erc20.set_maximum_allowance(result1[3])
#hflow.main.router.trade_single_hop(quote, signed_quote, effective_base_token_amount=10) 
#hflow.main.router.trade(quote2, signed_quote, tradeType=utils.Trade.eth_to_token)
#hflow.main.router.trade(quote3, signed_quote, tradeType=utils.Trade.tokens)
#print(hflow.main.pool.nonce(result3[0], operations))
#print(hflow.main.pool.flag(result3[0], 0))
