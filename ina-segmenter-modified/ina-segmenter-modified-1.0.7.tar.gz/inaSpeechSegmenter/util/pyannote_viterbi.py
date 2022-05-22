#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014-2016 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr

from __future__ import unicode_literals

from typing import Optional

import numba
import numpy as np

from numba import njit, int32, float32, int16

VITERBI_CONSTRAINT_NONE = int32(0)
VITERBI_CONSTRAINT_FORBIDDEN = int32(1)
VITERBI_CONSTRAINT_MANDATORY = int32(2)


LOG_ZERO = np.log(1e-45, dtype=np.float32)

# handling 'consecutive' constraints is achieved by duplicating states
# the following functions are here to help in this process


@njit(cache=True)
def _update_transition(transition: float32[:, :], consecutive: int16[:]) -> float32[:, :]:
    """
    Create new transition prob. matrix accounting for duplicated states.
    """
    # initialize with LOG_ZERO everywhere
    # except on the +1 diagonal np.log(1)
    new_n_states = int32(np.sum(consecutive))
    new_transition = LOG_ZERO * np.ones((new_n_states, new_n_states), dtype=np.float32)
    for i in range(1, new_n_states):
        new_transition[i - 1, i] = np.log(1)

    n_states = len(consecutive)
    boundary = np.hstack((np.array([0]), np.cumsum(consecutive)))
    start = boundary[:-1]
    end = boundary[1:] - 1

    for i in range(n_states):
        for j in range(n_states):
            new_transition[end[i], start[j]] = transition[i, j]

    return new_transition


@njit(cache=True)
def _update_initial(initial: float32[:], consecutive: int16[:]) -> float32[:]:
    """
    Create new initial prob. matrix accounting for duplicated states.
    """
    new_n_states = np.sum(consecutive)
    new_initial = LOG_ZERO * np.ones(new_n_states, dtype=np.float32)

    n_states = len(consecutive)
    boundary = np.hstack((np.array([0]), np.cumsum(consecutive)))
    start = boundary[:-1]

    for i in range(n_states):
        new_initial[start[i]] = initial[i]

    return new_initial


@njit(cache=True)
def _update_emission_constraint(ec: float32[:, :], consecutive: int16[:]) -> float32[:, :]:
    if np.max(consecutive) == 1:
        return ec

    nd = np.ones((int(np.sum(consecutive)), ec.shape[0]), dtype=np.float32)

    i = 0
    for ci in range(len(consecutive)):
        for _ in range(consecutive[ci]):
            nd[i, :] = ec[:, ci]
            i += 1
    return nd


@njit(cache=True)
def _update_states(states: int16[:], consecutive: int16[:]) -> float32[:]:
    """
    Convert sequence of duplicated states back to sequence of original states.
    """
    boundary = np.hstack((np.array([0]), np.cumsum(consecutive)))
    start = boundary[:-1]
    end = boundary[1:]

    new_states = np.empty(states.shape, dtype=np.float32)

    for i, (s, e) in enumerate(zip(start, end)):
        new_states[np.where((s <= states) & (states < e))] = i

    return new_states


@njit(cache=True)
def viterbi_decoding(emission: float32[:, :], transition: float32[:, :],
                     initial: Optional[float32[:]] = None, consecutive: Optional[int16] = None,
                     constraint: Optional[float32[:, :]] = None) -> float32[:]:
    """(Constrained) Viterbi decoding

    Parameters
    ----------
    emission : array of shape (n_samples, n_states)
        E[t, i] is the emission log-probabilities of sample t at state i.
    transition : array of shape (n_states, n_states)
        T[i, j] is the transition log-probabilities from state i to state j.
    initial : optional, array of shape (n_states, )
        I[i] is the initial log-probabilities of state i.
        Defaults to equal log-probabilities.
    consecutive : optional, int or int array of shape (n_states, )
        C[i] is a the minimum-consecutive-states constraint for state i.
        C[i] = 1 is equivalent to no constraint (default).
    constraint : optional, array of shape (n_samples, n_states)
        K[t, i] = 1 forbids state i at time t.
        K[t, i] = 2 forces state i at time t.
        Use K[t, i] = 0 for no constraint (default).

    Returns
    -------
    states : array of shape (n_samples, )
        Most probable state sequence

    """

    # ~~ INITIALIZATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    T, k = emission.shape  # number of observations x number of states

    # no minimum-consecutive-states constraints
    if consecutive is None:
        consecutive = np.ones(k, dtype=np.int16)

    # same value for all states
    elif isinstance(consecutive, int):
        consecutive = consecutive * np.ones(k, dtype=np.int16)

    # (potentially) different values per state
    else:
        consecutive = np.array(consecutive, dtype=np.int16).reshape((k, ))

    # at least one sample
    consecutive = np.maximum(1, consecutive)

    # balance initial probabilities when they are not provided
    if initial is None:
        initial = np.log(np.ones(k, dtype=np.float32) / k)

    # no constraint?
    if constraint is None:
        constraint = VITERBI_CONSTRAINT_NONE * np.ones((T, k), dtype=np.float32)

    # artificially create new states to account for 'consecutive' constraints
    emission = _update_emission_constraint(emission, consecutive)
    transition = _update_transition(transition, consecutive)
    initial = _update_initial(initial, consecutive)
    constraint = _update_emission_constraint(constraint, consecutive)
    T, K = emission.shape  # number of observations x number of new states
    states = np.arange(K)  # states 0 to K-1

    # set emission probability to zero for forbidden states
    emission = np.where(constraint != VITERBI_CONSTRAINT_FORBIDDEN, emission, LOG_ZERO)

    # set emission probability to zero for all states but the mandatory one
    tmp1 = emission[..., ::-1]
    emission = np.where(constraint != VITERBI_CONSTRAINT_MANDATORY, tmp1, LOG_ZERO)[..., ::-1]

    # ~~ FORWARD PASS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    V = np.empty((T, K), dtype=np.int32)  # V[t, k] is the probability of the
    V[0, :] = emission[0, :] + initial    # most probable state sequence for the
    # first t observations that has k as
    # its final state.

    P = np.empty((T, K), dtype=np.int32)  # P[t, k] remembers which state was used
    P[0, :] = states                      # to get from time t-1 to time t at
    # state k

    for t in range(1, T):

        # tmp[k, k'] is the probability of the most probable path
        # leading to state k at time t - 1, plus the probability of
        # transitioning from state k to state k' (at time t)
        tmp = (V[t - 1, :] + transition.T).T

        # optimal path to state k at t comes from state P[t, k] at t - 1
        # (find among all possible states at this time t)
        P[t, :] = np.argmax(tmp, axis=0)

        # update V for time t
        for i in states:
            V[t, i] = emission[t, i] + tmp[P[t, i], i]

    # ~~ BACK-TRACKING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    X = np.empty((T,), dtype=np.int16)
    X[-1] = np.argmax(V[-1, :])
    for t in range(1, T):
        X[-(t + 1)] = P[-t, X[-t]]

    # ~~ CONVERT BACK TO ORIGINAL STATES
    return _update_states(X, consecutive)


@njit(cache=True)
def viterbi_decoding_simple(emission: float32[:, :], transition: float32[:, :]) -> float32[:]:
    """
    Viterbi decoding without any optional arguments that the INA Segmenter code didn't use

    Parameters
    ----------
    emission : array of shape (n_samples, n_states)
        E[t, i] is the emission log-probabilities of sample t at state i.
    transition : array of shape (n_states, n_states)
        T[i, j] is the transition log-probabilities from state i to state j.

    Returns
    -------
    states : array of shape (n_samples, )
        Most probable state sequence
    """

    # ~~ INITIALIZATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    T, K = emission.shape  # number of observations x number of states

    # no minimum-consecutive-states constraints
    consecutive = np.ones(K, dtype=np.int16)

    # balance initial probabilities when they are not provided
    initial = np.log(np.ones(K, dtype=np.float32) / K)

    # artificially create new states to account for 'consecutive' constraints
    states = np.arange(K)  # states 0 to K-1

    # ~~ FORWARD PASS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    V = np.empty((T, K), dtype=np.int32)  # V[t, k] is the probability of the
    V[0, :] = emission[0, :] + initial    # most probable state sequence for the
    # first t observations that has k as
    # its final state.

    P = np.empty((T, K), dtype=np.int32)  # P[t, k] remembers which state was used
    P[0, :] = states                      # to get from time t-1 to time t at state k

    for t in range(1, T):

        # tmp[k, k'] is the probability of the most probable path
        # leading to state k at time t - 1, plus the probability of
        # transitioning from state k to state k' (at time t)
        tmp = (V[t - 1, :] + transition.T).T

        # optimal path to state k at t comes from state P[t, k] at t - 1
        # (find among all possible states at this time t)
        P[t, :] = np.argmax(tmp, axis=0)

        # update V for time t
        for i in states:
            V[t, i] = emission[t, i] + tmp[P[t, i], i]

    # ~~ BACK-TRACKING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    X = np.empty((T,), dtype=np.int16)
    X[-1] = np.argmax(V[-1, :])
    for t in range(1, T):
        X[-(t + 1)] = P[-t, X[-t]]

    # ~~ CONVERT BACK TO ORIGINAL STATES
    return _update_states(X, consecutive)
