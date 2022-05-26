# Copyright 2019-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# how to run a single test case:
# python -m unittest tests.test_docker.UbuntuDockerTest

from os.path import dirname, join
import time
from atelier.test import TestCase
import docker
import unittest

client = docker.from_env(version='auto')

class DockerTestMixin:
    docker_image = None
    remove_container = True
    tested_applications = ['cosi', 'noi', 'avanti']

    def setUp(self):
        if self.docker_image is None:
            return
        self.container = client.containers.run(
            self.docker_image, command="/bin/bash", user='lino', tty=True, detach=True)
            # self.docker_image, command="/bin/bash", user='lino', tty=True, detach=True)

    def tearDown(self):
        if self.docker_image is None:
            return
        self.container.stop()
        if self.remove_container:
            self.container.remove()

    def run_docker_command(self, command):
        # exit_code, output = container.exec_run(command, user='lino')
        print("===== run in {} {} : {} =====".format(self.docker_image, self.container, command))
        assert not '"' in command
        stream = True
        exit_code, output = self.container.exec_run(
            'bash -c "{}"'.format(command), user='lino',
            stdin=True, tty=True, stdout=True, stderr=True, stream=stream)
        if stream:
            lines = ''
            for ln in output:
                ln = ln.decode('utf-8')
                print(ln, end='')
                lines += ln
            return lines
        else:
            output = output.decode('utf-8')
            if exit_code != 0:
                msg = "%s  returned %d:\n-----\n%s\n-----" % (
                    command, exit_code, output)
                self.fail(msg)
            else:
                return output

    def do_test_contributor_env(self, application):
        """
        Test the instructions written on
        https://www.lino-framework.org/contrib/index.html
        """

        # TODO: this does not yet work. before going on, we need to meditate on
        # the docs as well.
        # https://www.lino-framework.org/team/install/index.html

        site_name = "{}1".format(application)
        self.run_docker_command(
            'mkdir ~/lino && virtualenv -p python3 ~/lino/env')
        res=self.run_docker_command('ls -l')
        self.assertIn('setup.py', res)
        self.run_docker_command("touch ~/.bash_aliases")
        cmdtpl = ". ~/lino/env/bin/activate && . ~/.bash_aliases && {}"
        # update pip to avoid warnings
        self.run_docker_command(cmdtpl.format('pip3 install -U pip'))
        # install getlino (the dev version)
        res = self.run_docker_command(cmdtpl.format('pip3 install -e .'))
        self.assertIn("Installing collected packages:", res)
        res = self.run_docker_command(cmdtpl.format(
            'getlino configure --clone --devtools --redis --batch '))
        self.assertIn('getlino configure completed', res)
        # print(self.run_docker_command(container, "cat ~/.lino_bash_aliases"))

        for application in self.tested_applications:
            site_name = "{}1".format(application)
            res = self.run_docker_command(cmdtpl.format(
                'getlino startsite {} {} --batch'.format(application, site_name)))
            self.assertIn(
                'The new site {} has been created.'.format(site_name), res)
            res=self.run_docker_command(cmdtpl.format(
                'go {} && . env/bin/activate && ls -l'.format(site_name)))
            print(res)
            res=self.run_docker_command(cmdtpl.format(
                '&& go {} && . env/bin/activate && pull.sh'.format(site_name)))
            print(res)

    def skipped_test_contributor_env(self):
        for application in self.tested_applications:
            self.do_test_contributor_env(application)

# @unittest.skip("20200727")
class UbuntuDockerTest(DockerTestMixin, TestCase):
    docker_image = "ubuntu_with_getlino"

    def test_developer_env(self):
        """
        Test the instructions written on
        https://dev.lino-framework.org/dev/install/index.html
        """
        venv = '~/lino/env'
        self.run_docker_command('mkdir ~/lino && virtualenv -p python3 {}'.format(venv))
        res = self.run_docker_command('ls -l')
        self.assertIn('setup.py', res)
        cmdtpl = '. {}/bin/activate'.format(venv)
        cmdtpl += " && {}"
        # update pip to avoid warnings
        self.run_docker_command(cmdtpl.format('pip3 install -U pip'))
        # install getlino (the dev version)
        res = self.run_docker_command(cmdtpl.format('pip3 install -e .'))
        self.assertIn("Installing collected packages:", res)

        def try_startsite(suffix):
            for app in self.tested_applications:
                site_name = "{}{}".format(app, suffix)
                cmd = 'getlino startsite {} {} --batch'.format(app, site_name)
                res = self.run_docker_command(cmdtpl.format(cmd))
                self.assertIn(
                    'The new site {} has been created.'.format(site_name), res)

        res = self.run_docker_command(
            cmdtpl.format('getlino configure --batch'))
        self.assertIn('getlino configure completed', res)
        # print(self.run_docker_command(container, "cat ~/.lino_bash_aliases"))

        try_startsite("m")

        res = self.run_docker_command(
            cmdtpl.format('getlino configure --batch --db-engine postgresql'))
        self.assertIn('getlino configure completed', res)
        # print(self.run_docker_command(container, "cat ~/.lino_bash_aliases"))

        try_startsite("p")


        # res = self.run_docker_command('. ~/.lino_bash_aliases && go {} && . env/bin/activate && ls -l'.format(site_name))
        # print(res)
        # res=self.run_docker_command('. ~/.lino_bash_aliases && go {} && . env/bin/activate && pull.sh'.format(site_name))
        # print(res)

#@unittest.skip("20200727")
class DebianDockerTest(DockerTestMixin, TestCase):
    docker_image = "debian_with_getlino"
    tested_applications = ['cosi', 'noi', 'avanti', 'voga', 'std']

    def test_production_server(self):
        """
        Test the instructions written on
        https://www.lino-framework.org/admin/install.html
        """
        # load bash aliases
        # res = self.run_docker_command(
        #    container, 'source /etc/getlino/lino_bash_aliases')
        res = self.run_docker_command('ls -l')
        self.assertIn('setup.py', res)
        # create and activate a master virtualenv
        self.run_docker_command('sudo mkdir -p /usr/local/lino/shared/env')
        self.run_docker_command(
            'cd /usr/local/lino/shared/env && sudo chown root:www-data . && sudo chmod g+ws . && virtualenv -p python3 master')
        mastercmd = ". /usr/local/lino/shared/env/master/bin/activate && {}"
        sudocmd = mastercmd.format("sudo env PATH=$PATH") + " {}"
        # update pip to avoid warnings
        self.run_docker_command(sudocmd.format('pip3 install -U pip'))
        # install getlino (the dev version)
        res = self.run_docker_command(sudocmd.format('pip3 install -e .'))
        self.assertIn("Installing collected packages:", res)
        # print(self.run_docker_command(container, "sudo cat /etc/getlino/lino_bash_aliases"))
        cmd = 'getlino configure --batch --monit'
        if True:
            cmd += " --web-server nginx"
        else:
            cmd += " --web-server apache"
        res = self.run_docker_command(sudocmd.format(cmd))
        self.assertIn('getlino configure completed', res)

        for application in self.tested_applications:
            site_name = "{}1".format(application)
            cmd = 'sudo env PATH=$PATH getlino startsite {} {} --batch'.format(application, site_name)
            res = self.run_docker_command(mastercmd.format(cmd))
            self.assertIn(
                'The new site {} has been created.'.format(site_name), res)
            cmdtpl = ". /etc/getlino/lino_bash_aliases && go {} && . env/bin/activate".format(site_name)
            cmdtpl += " && {}"
            # res = self.run_docker_command(cmdtpl.format('ls -l'))
            # print(res)
            # res = self.run_docker_command(cmdtpl.format('pull.sh'))
            # print(res)
            res = self.run_docker_command(cmdtpl.format('python manage.py prep --noinput'))
            print(res)
            res = self.run_docker_command(cmdtpl.format('./make_snapshot.sh'))
            print(res)
            # Wait up to STEP seconds for supervisor to finish restarting
            waiting = 120
            STEP = 2
            while waiting > 0:
                time.sleep(STEP)
                waiting -= STEP
                res = self.run_docker_command('/usr/local/bin/healthcheck.sh')
                if 'Error' in res or 'ERROR' in res:
                    continue
                else:
                    break
            if waiting > 0:
                self.fail("healthcheck.sh failed")

            cmd = '/etc/cron.daily/make_snapshot_{}.sh'.format(site_name)
            res = self.run_docker_command(cmd)
            print(res)

        # TODO : check whether the server is actually running
