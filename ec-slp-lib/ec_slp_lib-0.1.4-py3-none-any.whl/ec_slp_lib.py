#!/usr/bin/env python

"""Wrapper around Electron Cash wallet RPC commands

It uses substring along with RPC to manage Electron Cash wallet
"""

import json
import random
import subprocess
import sys
import configparser
import os.path
import requests
import os

__author__ = "uak"
__copyright__ = "Copyright 2022"
__credits__ = ["uak"]
__license__ = "LGPL"
__version__ = "3"


class EcSLP:
    """EC SLP class
    """
    
    def __init__(self, params):
        """
        Takes params dictionary as input and create instance variables from it.
        """
        #RPC parameters
        self.rpc_url= params.get("rpc_url")
        self.rpc_port= params.get("rpc_port")
        self.rpc_user= params.get("rpc_user")
        self.rpc_password= params.get("rpc_password")
        self.ec_config= params.get("ec_config")
        #Subprocess parameters
        self.python_path= params.get("python_path")
        self.electron_cash_path= params.get("electron_cash_path")
        self.wallet_path= params.get("wallet_path")
        self.network= params.get("network")
        self.use_custom_dir= params.get("use_custom_dir")
        self.custom_dir= params.get("custom_dir")   


    def set_rpc_port():
        """Set rpc port in Electron Cash config file
        """
        with open(self.ec_config, 'r+') as f:
            data = json.load(f)
            data["rpcport"] = self.rpc_port # <--- add `id` value.
            f.seek(0)        # <--- should reset file position to the beginning.
            json.dump(data, f, indent=4)
            f.truncate()     # remove remaining part
    
    
    def subprocessing(self, cmd, capture_output=True, text=True, run=False):
        """Function to run the wallet commads
        It checks the network specified in the config file then adds the flag accordingly
        """
        if self.network == "testnet":
            cmd = cmd + ("--testnet", )
        elif self.network == "mainnet":
            pass
        else:
            exit("No network specified")
        if self.use_custom_dir:
            cmd = cmd + ("--dir", self.custom_dir, )
        cmd = (self.python_path, self.electron_cash_path, *cmd)
        
        # ~ # Check configruation option super_user is set so it drop privileges
        # ~ if super_user:
            # ~ env = os.environ.copy()
            # ~ env.update({'HOME': home_dir, 'USER': user_name})
            # ~ return subprocess.check_output(cmd, preexec_fn=demote(os_uid, os_gid), env=env, text=text)
        # ~ else:
        if run:
            try:
                return subprocess.run(cmd, text=text)
            except Exception as err:
                raise
        else:
            try:
                return subprocess.check_output(cmd, text=text)
            except Exception as err:
                raise
    
    # ~ def demote(os_uid, os_gid):
        # ~ """Pass the function 'set_ids' to preexec_fn, rather than just calling
        # ~ setuid and setgid. This will change the ids for that subprocess only"""
    
        # ~ def set_ids():
            # ~ os.setgid(os_gid)
            # ~ os.setuid(os_uid)
    
        # ~ return set_ids
    
    
    def get_rpc_user_data(self):
        """
        Assign authantication data based on EC configuration.
        """
        config_dict["rpc_user"] = self.subprocessing(("getconfig","rpcuser")).rstrip()
        config_dict["rpc_password"] = self.subprocessing(("getconfig","rpcpassword")).rstrip()
        
    
    def ec_rpc(self, method, *args):
        """Use JSON-RPC interface to connect to the EC daemon
        """
    
        data = {
            "id":random.getrandbits(8), #uniqe number required by json specficiations
            "method":method,
            "params":[]
           }
    
        params = list(args)
        data["params"]=params
        try:
            response = requests.post(self.rpc_url+":"+str(self.rpc_port), json=data, auth=(self.rpc_user, self.rpc_password))
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.ConnectionError as err:
            raise Exception("RPC Connection Error")
        except requests.exceptions.HTTPError as err:
            raise Exception("RPC Authentication Error")
        except Exception as err:
            raise
    
        
        
    # Check if daemon is connected
    def check_daemon(self):
        """Check daemon running
        Checks if Electron Cash daemon is running
        """
        cmd = ("daemon", "status")
        try:
            daemon_status = self.subprocessing(cmd)
            json_output = json.loads(daemon_status)
            return "connected" in json_output
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            raise Exception("daemon is not connected")
    
    def start_daemon(self, run=True): # use subprocess run instead of checkout to avoid blocking of other commands
        """Start the daemon process
        """
        cmd = ("daemon", "start")
        
        try:
            return self.subprocessing(cmd, run=run)
        except Exception as err:
            raise
            # ~ return False
            
    def stop_daemon(self):
        """Stop the daemon process
        """
        cmd = ("daemon", "stop")
        
        try:
            return self.subprocessing(cmd)
        except Exception as err:
            raise
    
    def load_wallet(self, wallet_path):
        """Load the wallet file in the daemon
        """
        cmd = ("daemon", "load_wallet", "-w", wallet_path)
        return self.subprocessing(cmd)
    
    
    # Doesn't support multiple loaded wallet
    def check_wallet_loaded(self, wallet_path):
        """Check wallet loaded
        Checks if the wallet is loaded in Electron Cash daemon
        """
        cmd = ("daemon", "status")
        daemon_status = self.subprocessing(cmd)
        try:
            json_output = json.loads(daemon_status)
            # Check if wallet is loaded and return True or False
            return (wallet_path, True) in json_output["wallets"].items()
        except:
            raise Exception("wallet not loaded")

    def validate_address(self, address):
        """Validate Address"""
        return self.ec_rpc("validateaddress", address)["result"]
    
    def get_unused_bch_address(self):
        """Get unused BCH address"""
        return self.ec_rpc("getunusedaddress")["result"]
    
    
    def get_unused_slp_address(self):
        """Get unused SLP address"""
        return self.ec_rpc("getunusedaddress_slp")["result"]
    
    
    def get_bch_balance(self):
        """Get the total BCH balance in wallet"""
        return self.ec_rpc("getbalance")["result"]
    
    
    def get_address_balance_bch(self, address):
        """Get the balance of a BCH address"""
        return self.ec_rpc("getaddressbalance",address)["result"]
    
    
    def get_token_balance(self, token_id_hex):
        """Get the balance of a SLP token in wallet"""
        return self.ec_rpc("getbalance_slp", token_id_hex)["result"]
    
    
    def prepare_bch_transaction(self, address, bch_amount):
        """Prepare transaction
        Creates the raw transaction data
        """
        return self.ec_rpc("payto", address, bch_amount)["result"]
    
    
    def prepare_slp_transaction(self, token_id_hex, address_slp, token_amount):
        """Prepare SLP transaction
        Creates the raw SLP transaction data
        """
        return self.ec_rpc("payto_slp", token_id_hex, address_slp, token_amount)["result"]
    
    
    def broadcast_tx(self, tx_hex):
        """Broadcast transaction
        Send the transaction to the network
        """
        if int(tx_hex, 16):
            return self.ec_rpc("broadcast", tx_hex)["result"]
        else:
            raise Exception("error in hex string")
    
    def freeze_address(self, address):
        """Freeze an address so it can not be used later
        """
        return self.ec_rpc("freeze", address)["result"]
