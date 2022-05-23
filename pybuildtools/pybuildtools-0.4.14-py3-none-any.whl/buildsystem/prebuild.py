'''
Prebuild Wrapper Classes

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

@author: Rob
Created on May 14, 2015
'''

import os

from buildtools.bt_logging import log
from buildtools.lxml_utils import *
from lxml import etree
from buildtools.utils import getClassName


class BaseNode:
    def setAttr(self, element, name, skip_when_default=True, default=None, required=False):
        value = getattr(self, name, default)
        if value == default:
            if skip_when_default and not required:
                return
            if required:
                raise ValueError('{}: {} is not set, but is required.'.format(getClassName(self), name))
        element.set(name, value)

    def getAttr(self, element, name, required=False, default=None):
        value = element.get(name, None)
        if value is None:
            if required:
                raise ValueError('{}: {} is not set, but is required.'.format(getClassName(self), name))
            else:
                value = default
        setattr(self, name, value)


class Configuration(BaseNode):

    def __init__(self):
        self.options = {}
        self.name = ''

    def __contains__(self, name):
        return self.options.__contains__(name)

    def __getitem__(self, name):
        return self.options.__getitem__(name)

    def __delitem__(self, name):
        return self.options.__delitem__(name)

    def __setitem__(self, name, value):
        return self.options.__setitem__(name, value)

    def SerializeXML(self, parent):
        config = etree.SubElement(parent, 'Configuration', {'name': self.name})
        options = etree.SubElement(config, 'Options')
        for k, v in self.options.items():
            etree.SubElement(options, k).text = v

    @classmethod
    def DeserializeXML(cls, element):
        assert element.tag == 'Configuration'
        options = element[0]

        cfg = Configuration()
        for option in options:
            cfg[option.tag] = option.text
        return cfg


class Reference(BaseNode):

    def __init__(self):
        self.name = ''
        self.path = None

    def IsProjectReference(self):
        return self.path is None

    def SerializeXML(self, parent):
        ref = etree.SubElement(parent, "Reference", {'name': name})
        self.setAttr(ref, 'path')

    @classmethod
    def DeserializeXML(cls, element):
        assert element.tag == 'Reference'
        ref = Reference()
        ref.getAttr(element, 'name', required=True)
        ref.getAttr(element, 'path')
        return ref


class File(BaseNode):

    def __init__(self):
        self.path = ''
        self.buildAction = None
        self.filename = ''

    def SerializeXML(self, parent):
        f = etree.SubElement(self.files, 'File')
        f.text = self.filename
        self.setAttr(element, 'path')
        self.setAttr(element, 'buildAction', default='Compile')

    @classmethod
    def DeserializeXML(cls, element):
        assert element.tag == 'File'
        f = File()
        f.filename = element.text
        f.getAttr(element, 'path')
        f.getAttr(element, 'buildAction')


class Project(BaseNode):

    def __init__(self, solution=None, cfgNames=[]):
        self.solution = solution
        self.name = ''
        self.frameworkVersion = ''
        self.rootNamespace = ''
        self.type = ''
        self.path = ''

        self.configurations = {}
        self.referencePaths = []
        self.files = []
        self.references = []

    @classmethod
    def DeserializeXML(cls, element):
        assert element.tag == 'Project'

        proj = Project()
        proj.getAttr(element, 'frameworkVersion', required=True)
        proj.getAttr(element, 'name', required=True)
        proj.getAttr(element, 'type', required=True)
        proj.getAttr(element, 'path', required=True)

        proj.getAttr(element, 'rootNamespace')

        for child in element:
            if not etree.iselement(child) or child.tag is etree.Comment:
                continue
            if child.tag == 'Configuration':
                proj.configurations += [Configuration.DeserializeXML(child)]
            elif child.tag == 'ReferencePath':
                proj.referencePaths += [child.text]
            elif child.tag == 'Files':
                for filedata in child:
                    if not etree.iselement(filedata) or filedata.tag is etree.Comment:
                        continue
                    proj.files += [File.DeserializeXML(filedata)]
            elif child.tag == 'Reference':
                proj.references += [Reference.DeserializeXML(child)]
            else:
                log.error('!!! Unknown project tag child {}'.format(child.tag))

        return proj

    def set_config(self, buildtype, name, value):
        if buildtype not in self.configurations:
            self.configurations[buildtype] = Configuration()
        self.configurations[buildtype].set(name, value)

    def GetProjectDependencies(self):
        deps = []
        for ref in self.references:
            if ref.path is None:
                deps += [ref.name]
        return deps

    def SerializeXML(self):
        # <Project frameworkVersion="v4_0" name="Client" path="SS3D_Client" type="WinExe" rootNamespace="SS13">
        proj = etree.Element('Project')
        self.setAttr(proj, 'frameworkVersion', required=True)
        self.setAttr(proj, 'name', required=True)
        self.setAttr(proj, 'type', required=True)
        self.setAttr(proj, 'path', required=True)

        self.setAttr(proj, 'rootNamespace')

        for configuration in self.configurations:
            configuration.SerializeXML(self.tree)

        for refpath in self.referencePaths:
            etree.SubElement(self.tree, 'ReferencePath').text = refpath

        if len(self.files) > 0:
            files = etree.SubElement(self.tree, 'Files')
            for file in self.files:
                file.SerializeXML(files)

        if len(self.references) > 0:
            for ref in self.references:
                ref.SerializeXML(files)
        return f

    @classmethod
    def Load(cls, filename):
        proj = None
        with open(filename, 'r') as f:
            tree = etree.parse(f)
            root = tree.getroot()
            for elem in root.getiterator():
                if not hasattr(elem.tag, 'find'):
                    continue  # (1)
                i = elem.tag.find('}')
                if i >= 0:
                    elem.tag = elem.tag[i + 1:]
            proj = Project.DeserializeXML(root)
        return proj

    def Save(self, filename):
        with open(filename, 'w') as f:
            f.write(etree.tostring(self.tree, pretty_print=True, encoding='utf-8'))
        #print(' -> {}'.format(filename))


class Solution(BaseNode):

    def __init__(self, name=None, activeConfig='Debug', path='./', version=None):
        self.name = name
        self.activeConfig = activeConfig
        self.path = path
        self.version = version

        self.projects = {}
        self.configurations = {}

        self.project_deps = {}

    def calculateProjectOrder(self):
        self.project_deps = {}
        build_order = []
        longestPath = 0
        for _, proj in self.projects.items():
            self.project_deps[proj.name] = proj.GetProjectDependencies()

        for projName in project_deps.keys():
            deps = project_deps[projName]
            newDeps = []
            for dep in deps:
                if dep in self.projects:
                    newDeps += [dep]
            self.project_deps[projName] = newDeps

        projsLeft = len(projects)

        it = 0
        while projsLeft > 0:
            it += 1
            for projName in self.projects.keys():
                if projName in build_order:
                    continue
                deps = project_deps[projName]
                if len(deps) == 0:
                    build_order += [projName]
                    projsLeft -= 1
                    #print('[{}] Added {} (0 deps)'.format(it, projName))
                    continue

                defer = False
                for dep in deps:
                    if dep not in build_order:
                        defer = True
                        break
                if defer:
                    continue
                build_order += [projName]
                projsLeft -= 1
                #print('[{}] Added {} ({} deps)'.format(it, projName, len(deps)))

        return build_order

    def SerializeXML(self, inline_projects=False):
        #<Prebuild version="1.10" xmlns="http://dnpb.sourceforge.net/schemas/prebuild-1.10.xsd">
        #<Solution activeConfig="Debug" name="SpaceEngineersDedi64" path="./" version="0.0.1">
        root = e('Prebuild', {'version': '1.10', 'xmlns': 'http://dnpb.sourceforge.net/schemas/prebuild-1.10.xsd'})
        solution = etree.SubElement(root, 'Solution')
        # Required attributes
        for attrName in ['name', 'activeConfig', 'path', 'version']:
            self.setAttr(solution, attrName, required=True)

        for configuration in self.configurations:
            configuration.SerializeXML(solution)

        buildorder = self.calculateProjectOrder()

        for projectID in buildorder:
            solution.append(etree.Comment(text='Prerequisites: {}'.format(', '.join(sorted(self.project_deps[projectID])))))
            if inline_projects:
                solution.append(self.projects[projectID].SerializeXML())
            else:
                solution.append(etree.ProcessingInstruction('include', 'file="{}"'.format(os.path.join(self.projects[projectID].path, 'prebuild.xml'))))
