from testall import test_file, test_tree, test_tree_for, test_file_for
import os

def save_info():
    import subprocess
    for f in os.listdir('r:\\webdata\\clarify\\derived'):
        full_path = "r:\\webdata\\clarify\\derived\\%s\\libyarxi.so" % f
        if os.path.exists(full_path):
            with subprocess.Popen(['C:\\cygwin64\\bin\\readelf.exe', '--debug-dump=loc', '/cygdrive/r/webdata/clarify/derived/' + f + '/libyarxi.so'], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                stdout = proc.communicate()[0]
                if proc.returncode == 0:
                    with open("r:\\webdata\\clarify\\cliderived\\%s-loc.txt" % f, 'wt') as of:
                        of.write(str(stdout, 'ASCII'))

def dump_compiler(di):
    die = next(di.iter_CUs()).get_top_DIE()
    print(die.attributes['DW_AT_producer'].value.decode('UTF-8'))

test_file("samples\\sles_507.88")
#test_tree_for("\\\\sandbox\\seva\\webdata\\clarify\\derived", dump_compiler)    
#test_tree_for("\\\\mac\\seva\\quincy", dump_compiler)

#test_tree("samples")

def f(di):
    CUs = [cu for cu in di.iter_CUs()]
    CUs[24].get_top_DIE()

#test_file_for("samples\\ObjectiveDropboxOfficial.4.68.7.framework.dSYM", f) #CU24 - no top die???
#test_file("samples\ObjectiveDropboxOfficial.4.68.7.framework.dSYM") #DBTEAMGroupCreateError.m - no AT_name




#test_file('\\\\sandbox\\seva\\webdata\\clarify\\derived\\An-3.20.0-y-ARMv7\\libyarxi.so')
#test_file('\\\\mac\\seva\\quincy\\4.69.8\\YarxiMin.app.dSYM')
#test_tree('\\\\mac\\seva\\quincy')
#test_file('E:\\Seva\\Projects\\AnYarxi_3.43.5\\LibYarxi\\build\\intermediates\\ndkBuild\\yarxiRelease\\obj\\local\\x86\\libfakejipad.so')
#test_tree("\\\\sandbox\\seva\\webdata\\clarify\\derived")
#save_info()


# Find a file with a ranges under a CU with no low_pc
def nolopc(di):
    for CU in di.iter_CUs():
        if not 'DW_AT_low_pc' in CU.get_top_DIE().attributes:
            for die in CU.iter_DIEs():
                assert 'DW_AT_ranges' not in die.attributes

#test_tree_for('\\\\mac\\seva\\quincy', nolopc)
#test_tree_for("\\\\sandbox\\seva\\webdata\\clarify\\derived", nolopc)