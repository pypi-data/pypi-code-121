from wfgenes.core.initial_wfgenes import BasewfGenes
import os
import os.path
from copy import deepcopy
from collections import OrderedDict
import argparse
import json
import xmlschema
import yaml


class SimstackwfGenes(BasewfGenes):


    def __init__(self, blueargs):
        BasewfGenes.__init__(self, blueargs)
        self.wano_genrator()
        self.workflow_generator()
        self.pack_wano()


    def wano_genrator(self):
        for i in range(self.routine_number):
            self.simstack_path = os.path.join(self.workflow_path, 'SimStack')
            wano_path = os.path.join(self.simstack_path, 'wanos', self.routine_dir[i])
            if not os.path.exists(wano_path):
                os.makedirs(wano_path)
            xml_path = os.path.join(
                self.simstack_path,
                'wanos',
                self.routine_name[i],
                self.routine_name[i] +
                '.xml')    
            # Strat xml file generation
            file = open(xml_path, 'w')
            file.write('<WaNoTemplate>\n')
            file.write(" <WaNoRoot name='" + self.routine_name[i] + "'>\n")

            for j in range(self.subroutine_number[i]):
                for k in range(len(self.inputs_nodup[i][j])):
                    if self.inputs_nodup[i][j][k] != \
                            'duplicate' and self.inputs_no_locdep[i][j][k] != 'inner_dependent'\
                            and self.inputs_links[i][j][k][0].isnumeric() == False:
                        file.write(
                            "\t<WaNoFile name='" +
                            self.inputs_locname[i][j][k] +
                            " Data' logical_filename='" +
                            self.inputs_nodup[i][j][k] +
                            ".yaml' local='True'>" +
                            self.args_inputpath +
                            self.inputs_nodup[i][j][k] +
                            ".yaml</WaNoFile> \n")
                    elif self.inputs_nodup[i][j][k] != \
                        'duplicate' and self.inputs_no_locdep[i][j][k] != 'inner_dependent'\
                            and self.inputs_links[i][j][k][0].isnumeric():
                        path_dependent_output = os.path.join(self.routine_name[int(self.inputs_links[i][j][k][0])], self.outputs_locname[int(
                            self.inputs_links[i][j][k][0])][int(self.inputs_links[i][j][k][1])][int(self.inputs_links[i][j][k][2])] + '.yaml')
                        file.write(
                            "\t<WaNoFile name='" +
                             self.inputs_locname[i][j][k] +
                            " Data' logical_filename='" +
                             self.inputs_locname[i][j][k] +
                            ".yaml' local='False'>" +
                            path_dependent_output +
                            "</WaNoFile> \n")

            file.write(' </WaNoRoot>\n')
            file.write(
                " <WaNoExecCommand> bash ./run_python.sh</WaNoExecCommand>\n")
            file.write(" <WaNoInputFiles>\n")
            file.write("\t<WaNoInputFile logical_filename='run_python.sh'>"
                        "run_python.sh</WaNoInputFile>\n")
            file.write(
                "\t<WaNoInputFile logical_filename='" +
                self.routine_name[i] +
                "_wrapper.py'>" +
                self.routine_name[i] +
                "_wrapper.py</WaNoInputFile>\n")
            file.write(
                "\t<WaNoInputFile logical_filename='setenv.sh'>setenv.sh</WaNoInputFile>\n")
            file.write(" </WaNoInputFiles>\n")
            file.write(" <WaNoOutputFiles>\n")
            for j in range(self.subroutine_number[i]):
                for k in range(len( self.outputs_nodup[i][j])):
                    if  self.outputs_nodup[i][j][k] != 'duplicate':
                        file.write(
                            "\t<WaNoOutputFile logical_filename='" +
                             self.outputs_locname[i][j][k] +
                            ".yaml'>" +
                             self.outputs_locname[i][j][k] +
                            ".yaml</WaNoOutputFile>\n")
            file.write(" </WaNoOutputFiles>\n")
            file.write("</WaNoTemplate>")

            file.close()

            # Validate xml against schema
            schema_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                'xmlschema.xsd')
            my_schema = xmlschema.XMLSchema(schema_path)
            my_schema.validate(xml_path)

    def workflow_generator(self):
        
        simstack_wf_path = os.path.join(self.simstack_path, 'simstack.xml')
        file = open(simstack_wf_path, 'w')
        file.write('<root> \n')
        for i in range(self.routine_number):
            file.write(
                "\t <WaNo type='" +
                self.routine_name[i] +
                "' uuid='" +
                self.routine_name[i] +
                "' id='" +
                str(i) +
                "' name='" +
                self.routine_name[i] +
                "'/> \n")
        file.write('</root> \n')

        for i in range(self.routine_number):
            run_python_path = os.path.join(
                self.simstack_path, 'wanos', self.routine_name[i], 'run_python.sh')
            file = open(run_python_path, 'w')
            file.write("#!/bin/bash/ -ex \n")
            file.write("source setenv.sh \n")
            file.write("python " + self.routine_dir[i] + "_wrapper.py")

            file.close()

    def pack_wano(self):

        for i in range(self.routine_number):
            dest_path = os.path.join(
                self.simstack_path, 'wanos', self.routine_dir[i])
            source_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                'setenv.sh ')
            cmd = 'cp -r ' + source_path + dest_path+'/'
            os.popen(cmd)
            source_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                '..',
                'fig',
                'wano_fig.png ')
            cmd = 'cp ' + source_path + dest_path
            os.popen(cmd)
            source_path = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)),
                'resources.yml ')
            cmd = 'cp ' + source_path + dest_path
            os.popen(cmd)

    # End of WaNo Folder generation