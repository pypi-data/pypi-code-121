'''
BLURB GOES HERE.

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
class BaseProject(object):
    def __init__(self,name):
        self.name=name
        self.dependencies=[]
        self.provides=[]

    def Prepare(self,env):
        """
        Checks the global environment.

        Runs prior to any builds.
        :param BuildEnv env:
            Build environment.
        @return Success
        """
        return True

    def Configure(self,env):
        """
        Checks the build environment, configures package.

        Runs prior to project's build step.
        @return Success
        """
        return True

    def Build(self,env):
        """
        Builds the project. Configure is run before this step.
        @return Success
        """
        return True

    def Install(self,env):
        return True
