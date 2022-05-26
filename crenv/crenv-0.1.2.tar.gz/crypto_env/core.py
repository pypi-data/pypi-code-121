from abc import ABC, abstractclassmethod
from gym.spaces import Box, Dict, Discrete
import gym
import numpy as np

from crypto_env.types import Transaction, create_info_type
from crypto_env.dataloader.dataloader import DataLoader
from crypto_env.recorder import Recorder


class CryptoEnv(gym.Env, ABC):
    """
    This is the core module of `CrytoEnv`. It provide environment for agents to perform buy and sell actions and provide market states.
    """

    def __init__(self, max_sell, max_buy, min_sell, min_buy, dataloader: DataLoader,
                 recorder: Recorder):
        """__init__

        Args:
            max_sell (float): maximum crypto to sell
            max_buy (float): maximum crypto to buy
            min_sell (float): minimum crypto to sell
            min_buy (float): minimum crypto to buy
            dataloader (:py:class:`DataLoader`): the :py:class:`crypto_env.dataloader.dataloader.DataLoader` instance
            recorder (:py:class:`Recorder`): the :py:class:`Recorder` instance
        """        
        
        # transaction fees are not implemented in this environment. should be implemented in the algorithm (agent)
        super(CryptoEnv, self).__init__()

        assert (isinstance(dataloader, DataLoader))

        # check if transaction fee loaded
        if dataloader.get_transaction_fee_type() is None:
            raise Exception("Transaction fee not set.")

        self.dataloader = dataloader
        self._len_data = len(dataloader)
        self._len_features = len(dataloader._features)
        self.Info = create_info_type(dataloader._features)
        self.recorder = recorder
        self._max_sell = max_sell
        self._max_buy = max_buy
        self._min_sell = min_sell
        self._min_buy = min_buy
        self._is_fix_transaction_fee = dataloader.get_transaction_fee_type() == 'fix'
        
        # should be reset to False for each iteration
        self._is_done = False

        # define observation space: period market data. won't change due to action of the agent.
        self.observation_space = Dict({
            'index': Box(low=0, high=self._len_data - 1, shape=(1,),
                         dtype=np.int32),
            'features': Box(low=-np.inf,
                            high=np.inf,
                            shape=(len(self.dataloader._features),)),
        })

        # define action space:
        # signal: 0: buy, 1: sell, 2: hold.
        self.action_space = Dict({
            'signal': Discrete(3),
            'value': Box(low=min(self._min_buy, self._min_sell),
                         high=max(self._max_sell, self._max_buy),
                         shape=(1,))
        })

    def step(self, action=None):
        """step

        Args:
            action (dict, optional): action to take. Defaults to None.

        Returns:
            agent's observation after taking the action (numpy array),
            reward of the action (float),
            whether the episode is to the end (bool), and
            diagnostic information for debugging (any).
        """        
        
        # the history data will be returned as info from the recorder.
        signal = action['signal']
        value = action['value']
        transaction = Transaction(signal=signal, value=value[0])
        try:
            idx, info = next(self.dataloader)
        except StopIteration:
            idx = self.dataloader.idx + 1
            info = None
        observation = dict(
            features=np.array(list(info)),
            index=np.array([idx])
        )

        self.recorder.insert_transaction(transaction=transaction)
        self.recorder.insert_info(info=info)
        
        info = dict()
        if idx + 1 == len(self.dataloader):
            self._is_done = True
            
        reward = self.get_reward()

        return observation, reward, self._is_done, info
    
    @abstractclassmethod
    def get_reward(self):
        """get_reward

        Returns:
            float: the reward for agent after taking an action
        """        
        return 0.0

    def buy(self, value, verbose=0):
        """buy
        
        The agent buy some amount of crypto.

        Args:
            value (float): number of crypto to buy
            verbose (int, optional): whether to print out debug info. Defaults to 0.

        Returns:
            same return as :py:func:`step`
        """        
        fee_type = self.dataloader.get_transaction_fee_type()
        fee = self.dataloader.get_transaction_fee()
        if fee_type == 'fix':
            value -= value
        else:
            value = value * (1 - fee)
        action = dict(
            signal=0,
            value=np.array([value], dtype=np.float32)
        )
        # sanity check
        if value < self._min_buy or value > self._max_buy:
            action = dict(
                signal=2,
                value=np.array([0], dtype=np.float32)
            )
            if verbose:
                print("sell failed")

        return self.step(action)

    def sell(self, value, verbose=0):
        """sell
        
        The agent sell some amount of crypto.

        Args:
            value (float): number of crypto to sell
            verbose (int, optional): whether to print out debug info. Defaults to 0.

        Returns:
            same return as :py:func:`step`
        """        
        fee_type = self.dataloader.get_transaction_fee_type()
        fee = self.dataloader.get_transaction_fee()
        if fee_type == 'fix':
            value -= fee
        else:
            value = value * (1 - fee)
        action = dict(
            signal=1,
            value=np.array([value], dtype=np.float32)
        )
        # sanity check
        if value < self._min_sell or value > self._max_sell:
            action = dict(
                signal=2,
                value=np.array([0], dtype=np.float32)
            )
            if verbose:
                print("buy failed")

        return self.step(action)

    def hold(self, verbose=0):
        """hold
        
        The agent does not want to do anything in this step

        Args:
            verbose (int, optional): whether to print out debug info. Defaults to 0.

        Returns:
            same return as :py:func:`step`
        """        
        # hold will always be successful.
        action = dict(
            signal=2,
            value=np.array([0], dtype=np.float32)
        )
        return self.step(action)

    def first_observation(self):
        """Return the first observation

        Returns:
            dict: return a dictionary structured dict(features, index)
                    
        """        
        self.reset()
        idx, info = next(self.dataloader)
        observation = dict(
            features=np.array(list(info)),
            index=np.array([0])
        )
        return observation

    def reset(self):
        """Reset the environment to prepare for a new episode

        Returns:
            :py:class:`CryptoEnv`: 
            
        """        
        self.dataloader.reset()
        self.recorder.reset()
        self._is_done = False
        return self

    def render(self, mode="human"):
        """Placeholder. Not implemented yet.

        Args:
            mode (str, optional): Defaults to "human".
        """        
        pass

    def meta(self):
        """Return the meta information of the environment

        Returns:
            dict: the meta of the env
        """        
        # return meta information
        return dict(
            signals=dict(
                buy=0,
                sell=1,
                hold=2
            )
        )
