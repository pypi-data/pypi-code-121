import filecmp
import os


from clmgr.main import main

test_dir = os.path.dirname(os.path.realpath(__file__))

def test_single_java():
        global test_dir
        test_args = ['-c', test_dir + '/config/single.yml', '--file', test_dir + '/input/java/single.java', '--header-length', '120']
        main(test_args)
        assert filecmp.cmp(test_dir + '/input/java/single.java', test_dir + '/output/java/single.java', shallow=False)
