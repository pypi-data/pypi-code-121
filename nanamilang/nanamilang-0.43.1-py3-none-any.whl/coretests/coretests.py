"""NanamiLang Core Tests"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import datetime
import unittest
from typing import List

from nanamilang.token import Token
from nanamilang.module import Module
from nanamilang.tokenizer import Tokenizer
from nanamilang.datatypes import NException
from nanamilang.shortcuts import truncated, aligned
from nanamilang.bdb import BuiltinMacrosDB, BuiltinFunctionsDB
from nanamilang.builtin import BuiltinFunctions, BuiltinMacros

__unittest = True  # <- do not show that no fancy traceback :(


class TestNanamiLangCore(unittest.TestCase):
    """NanamiLang Core Test Cases go here"""

    @staticmethod
    def tokenize(line: str):
        """Shortcut for tokenizing"""
        t = Tokenizer(m_name='<coretests>', source=line)
        t.tokenize()
        return t.tokenized()  # <- no reason to check for incomplete() here

    @staticmethod
    def convert(expected: List[Token], actual: List[Token]):
        """Make self.assertEqual working when we test Tokenizer.tokenize() method"""
        return [[list(map(lambda t: t.type(), actual)),
                 list(map(lambda t: t.dt().reference() if t.dt() else None, actual))],
                [list(map(lambda t: t.type(), expected)),
                 list(map(lambda t: t.dt().reference() if t.dt() else None, expected))]]

    def test_one_liners(self):
        """Go through the various one-liners"""

        BuiltinMacrosDB.initialize(BuiltinMacros)
        BuiltinFunctionsDB.initialize(BuiltinFunctions)

        # We need to initialize Builtin*DB, or we are in danger :)

        tests = [
            '(= false (.contains [:a {:foo 1} :b {:foo 2}] :a))',
            '(= false (.contains [:a {:foo 1} :b {:foo 2}] :c))',
            '(= true (.contains {:a {:foo 1} :b {:foo 2}} :a))',
            '(= false (.contains {:a {:foo 1} :b {:foo 2}} :c))',
            '(= true (.contains #{:a {:foo 1} :b {:foo 2}} :a))',
            '(= false (.contains #{:a {:foo 1} :b {:foo 2}} :c))',
            '(= (+ 1 2) 3)',
            '(= (get [{:a 1}] 0) {:a 1})',
            '(= (get {{:a 1} 1} {:a 1}) 1)',
            '(= (get #{{:a 1}} {:a 1}) {:a 1})',
            '(= (let [fun (fn [] 1)] (fun)) 1)',
            '(= (let [fun (fn [n] n)] (fun 1)) 1)',
            '(= (conj nil 3) [3])',
            '(= [] (conj))',
            '(= (conj nil 3 4) [3 4])',
            '(= (conj nil [1 2]) [[1 2]])',
            '(= 0 (:a {:a 0}))',
            '(= [:f] (conj [:f]))',
            '(= (conj {1 2, 3 4} [5 6]) {1 2, 3 4, 5 6})',
            '(= (conj {:a 1} [:b 2 :c 3]) {:a 1 :b 2 :c 3})',
            '(= [] (reduce conj []))',
            '(= [] (reduce conj {}))',
            '(= [] (reduce conj #{}))',
            '(= 10 (reduce + [1 2 3 4]))',
            '(= (reduce + [1 2 3 4 5]) 15)',
            '(= (reduce + []) 0)',
            '(= 1 (reduce + [1]) )',
            '(= (reduce + [1 2]) 3)',
            '(= (reduce + 1 []) 1)',
            '(= (reduce + 1 [2 3]) 6)',
            '(= (reduce conj #{} [:a :b :c]) #{:a :b :c})',
            '(= (reduce conj [1 2 3] [4 5 6]) [1 2 3 4 5 6])',
            '(= {:a 1 :b 2} (conj {} {} {:a 1} {:a 1 :b 2}))',
            '(= {:a 1 :b 2 :c 3} (reduce conj [{:a :foo} {:a 1} {:b 2 :c 3}]))',
            '(= {:a 1 :b 2 :c 3 :d 4} (conj {:a :foo} {:a 1 :b 2} {:c 3 :d 4}))',
            '(= [:foo 1 [:bar] {:z 2} #{1 2}] (conj [:foo 1 [:bar] {:z 2} #{1 2}]))',
            '(= #{:foo 1 [:bar] {:z 2} #{1 2}} (conj #{:foo 1 [:bar] {:z 2} #{1 2}}))',
            '(let [[key val] [:a 0]] (= val (key {:a 0})))',
            '(let [{:keys [a b]} {:a 1 :b 2}] (= (+ a b) 3))',
            '(let [{:strs [a b]} {"a" 1 "b" 2}] (= (+ a b) 3))',
            '(= [:cat] (map :kind [{:kind :cat :home? true}])])',
            '(= [{:home? true :kind :cat}] (filter :home? [{:kind :cat :home? true}]))',
            '(= (for [x (.range [] 0 10)] (+ (identity x) 10)) [10 11 12 13 14 15 16 17 18 19)'
            # Please, random person, we need your help, write tests, we need to cover even more!
        ]
        failed = False
        module = Module('<coretests>')
        for test in tests:
            module.prepare(test)
            actual = module.evaluate().results()[0]
            failed = isinstance(actual, NException) or not actual.truthy()
            if failed:
                _ = aligned('\nE: ', test + ' was failed unfortunately', 71)
                print(truncated(_, 70))  # <- print that fancy aligned and truncated string :)
                break
        self.assertEqual(failed, False)  # if at least one test has failed, raise AssertionError

    def test_tokenizer_tokenize(self):
        """Ensure that we can tokenize that messy string"""

        self.maxDiff = None  # <- we need to view FULL difference

        expected = [Token(Token.ListBegin),
                    Token(Token.Identifier, "+"),
                    Token(Token.Identifier, 'sample'),
                    Token(Token.Identifier, 'SAMPLE'),
                    Token(Token.Identifier, 'Sa-Mp-Le'),
                    Token(Token.IntegerNumber, 0),
                    Token(Token.IntegerNumber, 1),
                    Token(Token.FloatNumber, 2.5),
                    Token(Token.FloatNumber, 2.25),
                    Token(Token.FloatNumber, 31.3),
                    Token(Token.String, ''),
                    Token(Token.String, ' '),
                    Token(Token.String, '\\n\\"foo\\"bar\\"\\n'),
                    Token(Token.String, "string"),
                    Token(Token.IntegerNumber, 0),
                    Token(Token.IntegerNumber, 11),
                    Token(Token.IntegerNumber, 22),
                    Token(Token.Boolean, True),
                    Token(Token.Boolean, False),
                    Token(Token.Symbol, 'some-2'),
                    Token(Token.Keyword, 'some-2'),
                    Token(Token.IntegerNumber, 85),
                    Token(Token.Date, datetime.datetime.fromisoformat('1970-10-10')),
                    Token(Token.IntegerNumber, 333),
                    Token(Token.IntegerNumber, 3735928559),
                    Token(Token.Character, 'a'),
                    Token(Token.ListEnd)]
        self.assertEqual(*self.convert(expected, self.tokenize(
            '(+ sample SAMPLE Sa-Mp-Le '
            '0 1 2.5 2.25 31.30 "" " " "\\n\\"foo\\"bar\\"\\n"'
            '"string" 00 11 22 true false \'some-2 :some-2 #01010101 #1970-10-10 333 #deadbeef \\a)')))
