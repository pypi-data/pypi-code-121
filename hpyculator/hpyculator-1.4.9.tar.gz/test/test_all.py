import tempfile
from typing import Any

import pytest

from hpyculator import hpycore, main_win_signal

test_reflect: Any = 0  # 初始化一个变量，用于检测结果


@pytest.mark.run(order=2)
def test_all():
    with tempfile.TemporaryFile("w+t", encoding="utf-8", errors="ignore") as filestream:
        bindSignalWithSlots()
        assert hpycore.setIoInstance(filestream) is None
        assert filestream is hpycore.getIoInstance()

        assert hpycore.addOne(1) == 2

        assert hpycore.setOutPutData(12) is None
        assert hpycore.getOutputData() == 12

        assert hpycore.write("test", end="test") is None
        assert hpycore.write_without_flush("test", end="test") is None
        assert hpycore.flush() is None
        filestream.seek(0)
        assert filestream.read() == "testtesttesttest"

    hpycore.output("test")
    assert test_reflect == "test"
    hpycore.clearOutput()
    assert test_reflect == 0
    hpycore.setOutput("test")
    assert test_reflect == "test"

    assert get_fun_name(1, 2, c=3) == (6, "get_fun_name")
    assert get_fun_runtime()[0] == 12


@pytest.mark.run(order=1)
def test_signal():
    bindSignalWithSlots()

    main_win_signal.appendOutPutBox.emit("appendOutPutBox")
    assert test_reflect == "appendOutPutBox"
    main_win_signal.clearOutPutBox.emit()
    assert test_reflect == 0
    main_win_signal.setOutPutBox.emit("setOutPutBox")
    assert test_reflect == "setOutPutBox"
    main_win_signal.getOutPutBox.emit()
    assert test_reflect == 1

    main_win_signal.setStartButtonText.emit("setStartButtonText")
    assert test_reflect == "setStartButtonText"
    main_win_signal.setStartButtonState.emit(True)
    assert test_reflect is True
    main_win_signal.setOutPutBoxCursor.emit("setOutPutBoxCursor")
    assert test_reflect == "setOutPutBoxCursor"


@hpycore.funName
def get_fun_name(a, b, __fun_name__, c=1):
    return (a + b + c, __fun_name__)


@hpycore.reRunTimes(12)
def get_fun_runtime():
    return 12


def bindSignalWithSlots():
    def appendOutPut(msg: str):
        global test_reflect
        test_reflect = msg

    def clearOutPut():
        global test_reflect
        test_reflect = 0

    def setOutPut(msg: str):
        global test_reflect
        test_reflect = msg

    def getOutPut():
        global test_reflect
        test_reflect = 1

    def setStartButtonText(msg: str):
        global test_reflect
        test_reflect = msg

    def setStartButtonState(state: bool):
        global test_reflect
        test_reflect = state

    def setOutPutBoxCursor(where: str):
        global test_reflect
        test_reflect = where

    # 自定义信号绑定函数
    main_win_signal.appendOutPutBox.connect(appendOutPut)
    main_win_signal.setOutPutBox.connect(setOutPut)
    main_win_signal.clearOutPutBox.connect(clearOutPut)
    main_win_signal.getOutPutBox.connect(getOutPut)
    main_win_signal.setStartButtonText.connect(setStartButtonText)
    main_win_signal.setStartButtonState.connect(setStartButtonState)
    main_win_signal.setOutPutBoxCursor.connect(setOutPutBoxCursor)
