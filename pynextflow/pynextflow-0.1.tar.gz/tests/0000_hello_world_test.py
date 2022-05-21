import pynextflow as nf


@nf.process(echo=True)
def hello(cheers: str) -> nf.bash:
    return f"echo {cheers}"


@nf.process(echo=True)
def pyhello(cheers: str, world: str):
    print(f"{cheers} {world}!")


#
# TESTS
#

from os.path import dirname, join


def test_hello_script():
    """
    Run a simple bash hello world pipeline
    """

    with nf.Nextflow(debug=True):
        script = hello(["hola", "hello", "ciao"])

    expected_script = join(dirname(__file__), "scripts", "0000_hello_world.nf")
    with open(expected_script, "rt") as fd:
        assert script == fd.read()


def test_hello_local(capfd):
    """
    Run a simple bash script locally
    """

    exit_code = hello("hola")

    assert exit_code == 0
    assert capfd.readouterr().out == "hola\n"


def test_pyhello_local(capsys):
    """
    Run a simple python script locally
    """

    pyhello("hola", "mon")

    assert capsys.readouterr().out == "hola mon!\n"


def test_pyhello_script():
    """
    Run a pure python pipeline
    """

    with nf.Nextflow(debug=True):
        script = pyhello(zip(["hola", "hello", "ciao"], ["mon", "world", "mondo"]))

    expected_script = join(dirname(__file__), "scripts", "0000_pyhello.nf")
    with open(expected_script, "rt") as fd:
        assert script == fd.read()


