import tempfile
from pyaiml21 import *
from pyaiml21.utils import *
import os
from pathlib import Path
from typing import List, Tuple
import re
import pytest
from dataclasses import dataclass, field
import glob
import sqlite3
import pymongo


USER_ID = "1"


IO = Tuple[str, str]
TestCase = List[IO]


@dataclass
class Inputs:
    aiml: list = field(default_factory=list)
    aimlif: list = field(default_factory=list)
    sets: dict = field(default_factory=dict)
    maps: dict = field(default_factory=dict)
    props: list = field(default_factory=list)
    subs: dict = field(default_factory=dict)


def load_bot(aiml_files: list, aimlif_files: list, sets: dict,
             maps: dict, props: list, subs: dict, **gm_kwargs):

    properties = dict()
    for path in props:
        properties.update(load_aiml_map(path))

    bot_sets = { name: load_aiml_set(path) for name, path in sets.items() }
    bot_maps = { name: load_aiml_map(path) for name, path in maps.items() }

    my_bot = Bot(**gm_kwargs)
    my_bot.add_properties(properties)
    for name, s in bot_sets.items():
        my_bot.config.sets[name] = s
    for name, m in bot_maps.items():
        my_bot.config.maps[name] = m

    for aiml in aiml_files:
        logger = my_bot.learn_aiml(aiml)
        assert not logger.has_errors(), str(logger.report())
        assert not logger.has_warnings(), str(logger.report())

    for aimlif in aimlif_files:
        logger = my_bot.learn_aimlif(aimlif)
        assert not logger.has_errors(), str(logger.report())
        assert not logger.has_warnings(), str(logger.report())

    for s, path in subs.items():
        su = load_aiml_sub(path)
        my_bot.add_substitutions(s, su)

    return my_bot


def bot_from_ti(ti: Inputs, **gm_kwargs):
    return load_bot(ti.aiml, ti.aimlif, ti.sets, ti.maps,
                    ti.props, ti.subs, **gm_kwargs)


def extract_test_cases(filename) -> List[TestCase]:
    result = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "/" not in line or '"' not in line:
                continue
            if not line.startswith("<!--") or not line.endswith("-->"):
                continue
            line = line[4:-4]
            inputs = re.findall(r'"([^"]*)"', line)
            assert len(inputs) % 2 == 0
            sequence = []
            for i in range(0, len(inputs), 2):
                sequence.append((inputs[i], inputs[i+1]))
            result.append(sequence)
    return result


def all_test_cases(ti: Inputs):
    result = []
    for file in ti.aiml:
        result.extend(extract_test_cases(file))
    return result


def run_separate(ti: Inputs):
    test_cases = all_test_cases(ti)
    for case in test_cases:
        my_bot = bot_from_ti(ti)
        for i, o in case:
            got = my_bot.respond(i, USER_ID)
            msg = f"Input: {i}\tExpected: {o}\tGot: {got}"
            assert got == o, msg


def run_together(ti: Inputs):
    test_cases = all_test_cases(ti)
    my_bot = bot_from_ti(ti)
    for case in test_cases:
        for i, o in case:
            got = my_bot.respond(i, USER_ID)
            msg = f"Input: {i}\tExpected: {o}\tGot: {got}"
            assert got == o, msg


##############################################################################

FOLDER = Path(os.path.dirname(__file__))  # current file directory

SETS = FOLDER / "sets"
MAPS = FOLDER / "maps"
AIML = FOLDER / "aiml"
AIMLIF = FOLDER / "aimlif"
PATTERNS = FOLDER / "pattern_matching"
PROPERTIES = FOLDER / "properties"
SUBS = FOLDER / "subs"


#
# Test 0: properties
#
TI_PROPS = Inputs(
    aiml=[str(PROPERTIES / "properties.test.aiml")],
    props=[str(PROPERTIES / "properties.txt")]
)


def test_sets():
    run_separate(TI_PROPS)


#
# Test 1: patterns
#
TI_PATTERNS = Inputs(
    aiml=[str(PATTERNS / "patterns.aiml")],
    props=[str(PATTERNS / "bot.properties")],
    sets={
        "city": str(PATTERNS / "city.set"),
        "color": str(PATTERNS / "color.set")
    }
)
TI_PATTERNS_THAT = Inputs(
    aiml=[str(PATTERNS / "pattern.that.topic.aiml")],
    props=[str(PATTERNS / "bot.properties")],
    sets={
        "city": str(PATTERNS / "city.set"),
        "color": str(PATTERNS / "color.set")
    }
)


def test_patterns():
    run_separate(TI_PATTERNS)


def test_patterns_with_that():
    run_separate(TI_PATTERNS_THAT)


#
# Test 2: maps
#
TI_MAPS = Inputs(
    aiml=[str(MAPS / "map.test.aiml")],
    maps={"tommorow": str(MAPS / "tommorow.map")},
    props=[str(MAPS / "props.txt")]
)


def test_maps():
    run_together(TI_MAPS)


#
# Test 3: sets
#
TI_SETS = Inputs(
    aiml=[str(SETS / "set.test.aiml")],
    sets={"days": str(SETS / "days.set")}
)


def test_sets():
    run_together(TI_SETS)


#
# Test 4: substitutions
#
TI_SUBS = Inputs(
    aiml=[str(SUBS / "substitutions.aiml")],
    subs={
        "normalize": str(SUBS / "normal.substitutions"),
        "denormalize": str(SUBS / "denormal.substitutions"),
        "gender": str(SUBS / "gender.substitutions"),
        "person": str(SUBS / "person.substitutions"),
        "person2": str(SUBS / "person2.substitutions")
    }
)

def test_subs():
    run_together(TI_SUBS)


#
# Test 5: aiml files
#
aiml_files = []
for file in glob.glob(str(AIML / "*.aiml")):
    aiml_files.append(file)

TI_AIML = Inputs(
    aiml=aiml_files
)

def test_aiml():
    run_together(TI_AIML)


#
# Test 6: aimlif files
#
aimlif_files = []
for file in glob.glob(str(AIMLIF / "*.aimlif")):
    aimlif_files.append(file)

TI_AIMLIF = Inputs(
    aimlif=aimlif_files
)

def test_aimlif():
    test_cases = extract_test_cases(str(AIMLIF / "inputs.txt"))
    my_bot = bot_from_ti(TI_AIMLIF)
    for case in test_cases:
        for i, o in case:
            got = my_bot.respond(i, USER_ID)
            msg = f"Input: {i}\tExpected: {o}\tGot: {got}"
            assert got == o, msg


#
# A) SQLITE
#

def test_sqlite_gm():
    with sqlite3.connect(":memory:") as conn:
        my_bot = bot_from_ti(TI_AIML, gm_cls=SqLiteGraphMaster, conn=conn)
        test_cases = all_test_cases(TI_AIML)
        for case in test_cases:
            for i, o in case:
                got = my_bot.respond(i, USER_ID)
                msg = f"Input: {i}\tExpected: {o}\tGot: {got}"
                assert got == o, msg


#
# B) MONGO
#

import logging
logging.basicConfig(level=logging.DEBUG)

try:
    tmp_client = pymongo.MongoClient()
    tmp_db = tmp_client.test_database
    collection = tmp_db.test_collection
    collection.insert_one({"hey": "a test"})
except:
    pass  # no mongo running on localhost
else:
    def test_mongo_gm():
        client = pymongo.MongoClient()
        db = client.test_database
        store_collection = db.data_aiml
        my_bot = bot_from_ti(TI_AIML, gm_cls=MongoGraphMaster, collection=store_collection)
        test_cases = all_test_cases(TI_AIML)
        for case in test_cases:
            for i, o in case:
                got = my_bot.respond(i, USER_ID)
                msg = f"Input: {i}\tExpected: {o}\tGot: {got}"
                assert got == o, msg
