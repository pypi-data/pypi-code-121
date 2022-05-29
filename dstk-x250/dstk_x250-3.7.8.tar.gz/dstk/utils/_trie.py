#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structure graphe de type trie
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Created on Sun Feb 13 14:52:34 2022

@author: Cyrile Delestre
"""

from __future__ import annotations
from typing import Any, Dict
from functools import reduce

class Trie(dict):
    r"""
    Arbre simple de type trie construit sur la base des dictionnaires Python.
    Permet de construire des arbres et la gestion des noeuds manquants ce
    fait de manière transparente. Il est possible de bloquer la strcuture
    afin de figer le trie.

    Examples
    --------
    >>> from dstk.utils import Trie
    >>> 
    >>> trie = Trie()
    >>> trie.default_fields = dict(loss=None, val='test')
    >>> trie
        {}
    >>> trie['a']['b']['c'] = 42
    >>> trie
        {
            'a': {
                'loss': None,
                'val': 'test',
                'b': {
                    'loss': None,
                    'val': 'test',
                    'c': 42
                }
            }
        }
    >>> 
    >>> trie.insert(*"cd", q=42)
    >>> trie
        {
            'a': {
                'loss': None,
                'val': 'test',
                'b': {
                    'loss': None,
                    'val': 'test',
                    'c': 42
                }
            },
            'c': {
                'loss': None,
                'val': 'test',
                'd': {
                    'loss': None,
                    'val': 'test',
                    'q': 42
                }
            }
        }
    >>> 
    >>> trie.lock
    >>> trie['q']
        KeyError: "La clef q n'existe pas."

    Il est également possible de checker facilement si un noeud est terminal.
    Pour ça il suffit d'utiliser l'attribue
    :attr:`~dstk.utils._trie.Trie.isleaf`, en reprennant l'exemple ci-dessus :

    >>> trie.isleaf
        False
    >>> trie['a'].isleaf
        False
    >>> trie['a']['b'].isleaf
        True
    >>> trie['c'].isleaf
        False
    >>> trie['c']['d'].isleaf
        True

    Il est également possible de partir d'une structure existante en Python
    de construire un objet Trie grace à l'initalisation via la méthode de
    classe :func:`~dstk.utils._trie.Trie.deep_init` :

    >>> graph_dict = dict(a=dict(loss=42), b=0.42)
    >>> trie = Trie.deep_init(graph=graph_dict)
    >>> trie.isleaf
        False
    >>> trie['a'].isleaf
        True

    Warnings
    --------
    La valeur par défaut des noeuds est un dictionnaire vide, penser à faire :

    >>> trie.default_fields = dict(...)

    pour chancher ce comportement.
    """
    _lock: bool = False
    _default_fields: Dict[str, Any] = dict()
    _leaf: bool = True

    def __missing__(self, key: Any) -> Trie:
        r"""
        Permet de créer un noeud de type Trie si l'instance n'existe pas.
        Méthode facile pour créer un arbre.

        Parameters
        ----------
        key: Any
            clef d'accès à l'instance du dictionnaire.
        """
        if not self._lock:
            self._leaf = False
            val = self[key] = self.__class__(**self.default_fields)
            self[key].default_fields = self.default_fields
            return val
        raise KeyError(f"La clef {key} n'existe pas.")

    def __setitem__(self, key, v):
        r"""
        Méthode interne d'insertion dans un dictionnaire et permet de passer
        le filtre de verrouillage du graphe ou non.
        """
        if not self._lock:
            super().__setitem__(key, v)
        else:
            raise KeyError(f"La clef {key} n'existe pas.")

    @property
    def default_fields(self) -> Dict[str, Any]:
        r"""
        Accesseur aux champs par défaut à chaque nouveau Noeud de l'arbre.
        """
        return self._default_fields

    @default_fields.setter
    def default_fields(self, default_fields):
        r"""
        Permet de définir le champs par défaut.
        """
        self._default_fields = default_fields
        for key in self:
            if hasattr(self[key], '_default_fields'):
                self[key].default_fields = default_fields

    @property
    def lock(self):
        r"""
        Permet de vérouille la construction du Trie.
        """
        self._lock = True
        for key in self:
            if hasattr(self[key], '_lock'):
                self[key].lock

    @property
    def unlock(self):
        r"""
        Permet de dévérouiller la construction du Trie.
        """
        self._lock = False
        for key in self:
            if hasattr(self[key], '_lock'):
                self[key].unlock

    @classmethod
    def deep_init(
        cls,
        graph: Dict[str, Any],
        default_fields: Dict[str, Any]=dict(),
        del_rec: bool=False
    ) -> Trie:
        r"""
        Méthode de classe permettant de créé un Trie a partir d'éléments
        encapsuler dans un dictionnaire.

        Parameters
        ----------
        graph: Dict[str, Any]
            Structure du graphe trie au format dictionnaire Python.
        default_fields: Dict[str, Any] (=dict())
            Champs par défaut durant la création d'un noeud.
        del_rec: bool (=False)
            Efface récurcivement les données du modèle graph, ceci permet
            de préserver la mémoire si le graphe est très gros.
        """
        if not isinstance(graph, dict):
            raise AttributeError("graph doit être un dictionnaire.")
        trie = cls()
        trie.default_fields = default_fields
        trie._deep_init(graph, del_rec)
        return trie

    def _deep_init(self, graph: Dict[str, Any], del_rec: bool):
        r"""
        Méthode récurrente pour propager les objets Trie dans l'arborescence.
        """
        for key in list(graph):
            if isinstance(graph[key], dict):
                self[key]._deep_init(graph[key], del_rec)
            else:
                self[key] = graph[key]
            if del_rec: del graph[key]

    @property
    def islock(self) -> bool:
        r"""
        Retourne l'état de lockage du Trie.

        Warnings
        --------
        Test seulement un noeud, mais la procédure le lock est propagé à
        tous les noeuds, donc si un est locké, ils le sont tous.
        """
        return self._lock

    @property
    def isleaf(self) -> bool:
        r"""
        Renvoit True si le noeud est terminale (est une feuille), False sinon.
        """
        return self._leaf

    def access(self, *args) -> Any:
        r"""
        Méthode d'accès rapide à un élément du Trie. Si le Trie est 
        dévérouillé et que les noeuds d'accès à l'élément n'existe pas il sera
        créé, sinon une erreur KeyError sera émis.

        *args
            itérateur des arguments d'accès.

        Example
        -------
        >>> trie['a']['b']['c']
        >>> 42

        est équivalent à

        >>> trie.access(*"abc")
        >>> 42
        """
        return reduce(lambda x, y: x[y], args[1:], self[args[0]])

    def insert(self, *args, **kargs) -> None:
        r"""
        Méthode facilitant l'incertion d'un élément dans le Trie. Si le Trie
        est dévérouillé et que l'insersion utilise des noeuds qui n'existent
        pas dans le Trie alors il sera créé, sinon une erreur KeyError sera
        émis.

        Parameters
        ----------
        idx: int
            Valeur à entré au niveau de la feuille (argument 'idx').
        loss: float
            Valeur de la fonction coût calculé par l'apprentissage 
            (argument 'loss').
        *args :
            itérateur des arguments d'accès.

        Example
        -------
        >>> trie['a']['b']['c']['idx'] = 42
        >>> trie['a']['b']['c']['loss'] = 0.42

        est équivalent à

        >>> trie.insert(*"abc", idx=42, loss=0.42)
        """
        leaf = self.access(*args)
        for kk, vv in kargs.items():
            leaf[kk] = vv
