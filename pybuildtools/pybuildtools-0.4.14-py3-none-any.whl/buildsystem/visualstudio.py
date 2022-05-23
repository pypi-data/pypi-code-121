'''
Visual Studio tools and wrappers

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
'''
import codecs
import re
import uuid
import collections

from typing import Tuple

from lxml import etree
from lxml.etree import QName

from buildtools.bt_logging import log


VSNS = "http://schemas.microsoft.com/developer/msbuild/2003"

REG_FIND_BAD_SELFCLOSERS = re.compile(r'([^ ])/>')
FIX_BAD_SELFCLOSERS = '\\1 />'
REG_SECTIONPARSE = re.compile(
    r'[a-zA-Z]+\((?P<name>[^\)]+)\) = (?P<type>[a-zA-Z]+)')
#{579B8F56-49F6-4B9D-8013-E11F69E5308C}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
REG_PROJECTCONF = re.compile(
    r'(?P<project>\{[A-Z0-9\-]+\})\.(?P<cfgA>[A-Za-z0-9 \|]+)\.(?P<confType>[A-Za-z0-9\.]+) = (?P<cfgB>[A-Za-z0-9 \|]+)')


def setElementValue(parent, elementName, value):
    e = parent.find(elementName)
    if e is None:
        e = etree.Element(elementName)
        parent.append(e)
    e.text = value


def getElementValue(parent, elementName):
    e = parent.find(elementName)
    if e is None:
        return None
    return e.text


def _addSubelementProperty(elementName):
    return property(fget=lambda self: getElementValue(self.element, elementName), fset=lambda self, value: setElementValue(self.element, elementName, value))


def _addAttributeProperty(elementName):
    return property(fget=lambda self: self.element.attrib[elementName], fset=lambda self, value: self.element.attrib.set(elementName, value))


class BaseProjectElement(object):
    def __init__(self, project, element):
        self.project = project
        self.element = element

    Condition = _addAttributeProperty('Condition')


class OperationType:
    NONE = 'None'
    COMPILE = 'Compile'


class CopyToOutputDirectoryMode:
    Always = 'Always'
    Never = 'Never'
    PreserveNewest = 'PreserveNewest'


class BaseFileOperation(BaseProjectElement):
    def __init__(self, project, element):
        super(BaseFileOperation, self).__init__(project, element)

    @property
    def Operation(self):
        return self.element.tag

    @Operation.setter
    def Operation_set(self, value):
        self.element.tag = value

    DependentUpon = _addSubelementProperty('DependentUpon')
    AutoGen = _addSubelementProperty('AutoGen')
    Visible = _addSubelementProperty('Visible')
    # <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    CopyToOutputDirectory = _addSubelementProperty('CopyToOutputDirectory')

    Include = _addAttributeProperty('Include')


class CompileOperation(BaseFileOperation):
    def __init__(self, project, element):
        super(CompileOperation, self).__init__(project, element)


class EmbeddedResourceOperation(BaseFileOperation):
    def __init__(self, project, element):
        super(EmbeddedResourceOperation, self).__init__(project, element)

    Generator = _addSubelementProperty('Generator')
    LastGenOutput = _addSubelementProperty('LastGenOutput')
    CustomToolNamespace = _addSubelementProperty('CustomToolNamespace')
    LogicalName = _addSubelementProperty('LogicalName')
    Link = _addSubelementProperty('Link')


class BaseReference(BaseProjectElement):
    def __init__(self, project, element):
        super(BaseReference, self).__init__(project, element)

    @property
    def RefID(self):
        return ''


class AssemblyReference(BaseReference):
    def __init__(self, project, element):
        super(AssemblyReference, self).__init__(project, element)

    @property
    def RefID(self):
        return self.Include.split(',')[0].strip()

    Include = _addAttributeProperty('Include')
    # Needs special handling.
    #Private = _addSubelementProperty('Private')
    HintPath = _addSubelementProperty('HintPath')

    @property
    def Private(self):
        return getElementValue(self.element, 'Private') == 'true'

    @Private.setter
    def Private_set(self, value):
        setElementValue(self.element, 'Private', 'true' if value else "false")


class ProjectReference(BaseReference):
    def __init__(self, project, element):
        super(ProjectReference, self).__init__(project, element)

    @property
    def RefID(self):
        return self.Include if (self.Name is None or self.Name == '') else self.Name

    Include = _addAttributeProperty('Include')
    Project = _addSubelementProperty('Project')
    Name = _addSubelementProperty('Name')


class PropertyGroup(BaseProjectElement):
    def __init__(self, project, element):
        super(PropertyGroup, self).__init__(project, element)

    def __getitem__(self, elemName):
        return getElementValue(self.element, elemName)

    def __setitem__(self, elemName, value):
        setElementValue(self.element, elemName, value)

    # def setitem(self,a,value):
    #    setElementValue(self.element,a,value)


class VS2015Project(object):
    def __init__(self):
        self.PropertyGroups = []
        self.ReferencesByName = {}
        self.References = []
        self.Files = []

        self._referenceGroup = None
        self._projectReferenceGroup = None
        self._project = None
        self._namespace = None
        self._compileItemGroup = None
        self._noneItemGroup = None
        self._embeddedResourceItemGroup = None

    def LoadFromFile(self, filename):
        # with codecs.open(filename, 'r', encoding='utf-8-sig') as f:
        it = etree.iterparse(filename)
        for _, el in it:
            if '}' in el.tag:
                el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        self._project = it.root
        # self._project=etree.parse(f)
        self.ReloadEverything()

    def ReloadEverything(self):
        self.PropertyGroups = []
        self.ReferencesByName = {}
        self.References = []
        self.Files = []

        self._referenceGroup = None
        self._projectReferenceGroup = None
        # self._project=None
        self._namespace = None
        self._compileItemGroup = None
        self._noneItemGroup = None
        self._embeddedResourceItemGroup = None

        for node in self._project.iter():
            if node.tag == 'Reference':
                reference = AssemblyReference(self, node)
                self.ReferencesByName[reference.RefID] = reference
                self.References.append(reference)
                self._referenceGroup = node.getparent()
            elif node.tag == 'ProjectReference':
                projectReference = ProjectReference(self, node)
                self.ReferencesByName[projectReference.RefID] = projectReference
                self.References.append(projectReference)
                self._projectReferenceGroup = node.getparent()
            elif node.tag == 'PropertyGroup':
                self.PropertyGroups.append(PropertyGroup(self, node))
            elif node.tag == "Compile":
                self._compileItemGroup = node.getparent()
                self.Files.append(CompileOperation(self, node))
            elif node.tag == "None":
                self._noneItemGroup = node.getparent()
                self.Files.append(BaseFileOperation(self, node))
            elif node.tag == "EmbeddedResource":
                self._embeddedResourceItemGroup = node.getparent()
                self.Files.append(EmbeddedResourceOperation(self, node))

    def SaveToFile(self, filename):
        for node in self._project.iter():
            node.tag = QName(VSNS, node.tag)
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            f.write(REG_FIND_BAD_SELFCLOSERS.sub(FIX_BAD_SELFCLOSERS, etree.tounicode(
                self._project, pretty_print=True, xml_declaration=True)))

    def HasReference(self, refID):
        if refID in self.ReferencesByName:
            return True
        for ref in self.References:
            if ref.RefID == refID:
                return True
        return False

    def AddAssemblyRef(self, refID, hintpath, verbose=False):
        if verbose:
            log.info('Adding assembly reference %s.', refID)
        reference = self.subelement(self._referenceGroup, 'Reference')
        asmRef = AssemblyReference(self, reference)
        asmRef.Include = refID
        asmRef.HintPath = hintpath
        self.ReferencesByName[asmRef.RefID] = asmRef
        self.References.append(asmRef)
        return asmRef

    def AddProjectRef(self, include, name, guid, verbose=False):
        if verbose:
            log.info('Adding project reference %s.', name)
        reference = self.subelement(
            self._projectReferenceGroup, "ProjectReference")
        projRef = ProjectReference(self, reference)
        self.ReferencesByName[projRef.RefID] = projRef
        self.References.append(projRef)
        projRef.Name = name
        projRef.Include = include
        projRef.Project = guid
        return projRef

    def GetReference(self, refID):
        return self.ReferencesByName[refID]

    def RemoveReference(self, refID):
        if refID in self.ReferencesByName:
            del self.ReferencesByName[refID]
        nRemoved = 0
        for ref in list(self.References):
            if ref.RefID != refID:
                continue
            ref.Remove()
            self.References.remove(ref)
            nRemoved += 1
        return nRemoved

    def RemoveDuplicates(self):
        nRemoved = 0
        for refID in self.ReferencesByName.keys():
            for ref in list(self.References):
                if refID != ref.RefID:
                    continue
                if ref != self.ReferencesByName[refID]:
                    continue
                ref.Remove()
                self.References.remove(ref)
                nRemoved += 1
        return nRemoved

    def subelement(self, refgroup, tag):
        child = etree.Element(tag)
        refgroup.append(child)
        return child


class ProjectType(object):
    SOLUTION_FOLDER = '{2150E333-8FDC-42A3-9474-1A3956D46DE8}'
    CSHARP_PROJECT = '{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}'


class SolutionProject(object):
    def __init__(self):
        self.guid = ''
        self.type = ''
        self.name = ''
        self.projectfile = ''
        self.dependencies = []
        self.children = []
        self.solutionItems = []
        # solution => [activeCfg, build.0?]
        self.configurations = collections.OrderedDict()


class ProjectSections:
    ProjectDependencies = 'ProjectDependencies'
    SolutionItems = 'SolutionItems'


ProjectSectionTypes = {
    ProjectSections.ProjectDependencies: 'postProject',
    ProjectSections.SolutionItems: 'preProject'
}


class GlobalSections:
    SolutionConfigurationPlatforms = 'SolutionConfigurationPlatforms'
    ProjectConfigurationPlatforms = 'ProjectConfigurationPlatforms'
    SolutionProperties = 'SolutionProperties'
    NestedProjects = 'NestedProjects'


GlobalSectionTypes = {
    GlobalSections.SolutionConfigurationPlatforms: 'preSolution',
    GlobalSections.SolutionProperties: 'preSolution',
    GlobalSections.NestedProjects: 'preSolution',

    GlobalSections.ProjectConfigurationPlatforms: 'postSolution',
}

# NOT XML.


class Solution(object):
    '''
    A logical representation of a Visual Studio solution file.

    @author Rob Nelson
    '''

    '''
    Here for reference.
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio 2013
VisualStudioVersion = 12.0.21005.1
MinimumVisualStudioVersion = 10.0.40219.1
Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "Game Modes", "Game Modes", "{512B02AB-C927-4F3F-A7BF-26E6EE4CF678}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "DarkSouls.ModScript", "DarkSouls.ModScript\DarkSouls.ModScript.csproj", "{6929FE32-25FE-4893-8398-274A2BA6B8E2}"
    ProjectSection(ProjectDependencies) = postProject
        {BC0CE12E-0DB2-4BFF-8752-CEAF6EF9B30F} = {BC0CE12E-0DB2-4BFF-8752-CEAF6EF9B30F}
    EndProjectSection
EndProject
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
        Debug|Any CPU = Debug|Any CPU
        Release|Any CPU = Release|Any CPU
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
        {579B8F56-49F6-4B9D-8013-E11F69E5308C}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
        {579B8F56-49F6-4B9D-8013-E11F69E5308C}.Debug|Any CPU.Build.0 = Debug|Any CPU
        {579B8F56-49F6-4B9D-8013-E11F69E5308C}.Release|Any CPU.ActiveCfg = Release|Any CPU
        {579B8F56-49F6-4B9D-8013-E11F69E5308C}.Release|Any CPU.Build.0 = Release|Any CPU
    EndGlobalSection
    GlobalSection(SolutionProperties) = preSolution
        HideSolutionNode = FALSE
    EndGlobalSection
    GlobalSection(NestedProjects) = preSolution
        {BD5A9056-F832-4DE4-97B2-38AB62342382} = {512B02AB-C927-4F3F-A7BF-26E6EE4CF678}
    EndGlobalSection
EndGlobal
    '''

    def __init__(self):
        self.formatVersion = ''  # 12.00
        self.vsYear = ''  # 2013
        self.vsVersion = ''  # 12.0.21005.1
        self.minVSVersion = ''  # 10.0.40219.1

        self.projects = []
        self.projectsByGUID = {}
        self.projectsByName = {}

        self.properties = {
            'HideSolutionNode': 'FALSE'
        }

        self.configurations = []

    def getProjectDeclHeader(self, project):
        return 'Project("{type}") = "{name}", "{projectfile}", "{guid}"'.format(type=project.type, name=project.name, projectfile=project.projectfile, guid=project.guid)

    def getProjectDeclFooter(self):
        return 'EndProject'

    def getProjectSectionStart(self, name):
        return '\tProjectSection({}) = {}'.format(name, ProjectSectionTypes[name])

    def getProjectSectionEnd(self):
        return '\tEndProjectSection'

    def getGlobalSectionStart(self, name):
        return '\tGlobalSection({}) = {}'.format(name, GlobalSectionTypes[name])

    def getGlobalSectionEnd(self):
        return '\tEndGlobalSection'

    def AddProject(self, name, typeGUID, location=None, guid=None):
        if location is None:
            location = name
        project = SolutionProject()
        project.name = name
        project.type = typeGUID
        project.projectfile = location
        project.guid = guid or '{{{}}}'.format(str(uuid.uuid4()).upper())
        self.projects.append(project)
        self.projectsByGUID[project.guid] = project
        self.projectsByName[project.name] = project

        # Inherit defaults from solution.
        for cfg in self.configurations:
            project.configurations[cfg] = {'ActiveCfg': cfg, 'Build.0': cfg}

        return project

    def LoadFromFile(self, filename):
        with codecs.open(filename, 'r', encoding='utf-8-sig') as f:
            state = 'Header'
            project: SolutionProject = None
            section: Tuple[str, str] = None
            for line in f:
                oline = line
                line = line.strip()
                if state == 'Header':
                    if line.startswith('Microsoft Visual Studio Solution File'):
                        self.formatVersion = line.split(' ')[-1]
                    if line.startswith('# Visual Studio '):
                        self.vsYear = ' '.join(line.split(' ')[2:])
                    if line.startswith('VisualStudioVersion = '):
                        self.vsVersion = line.split(' ')[-1]
                    if line.startswith('MinimumVisualStudioVersion = '):
                        self.minVSVersion = line.split(' ')[-1]
                        state = 'Projects'
                elif state == 'Projects':
                    if line.startswith('Project('):
                        project = SolutionProject()
                        project.type = line[9:47]
                        project.name, project.projectfile, project.guid = [
                            x.strip().strip('"') for x in line.split('=')[1].strip().split(',')]
                        self.projects.append(project)
                        self.projectsByGUID[project.guid] = project
                        self.projectsByName[project.name] = project
                    elif line == 'EndProject':
                        project = None
                    elif line.startswith('ProjectSection('):
                        m = REG_SECTIONPARSE.match(line)
                        if m is not None:
                            section = (m.group('name'), m.group('type'))
                    elif line == 'EndProjectSection':
                        section = None
                    elif line == 'Global':
                        for project in self.projects:
                            project.dependencies = [
                                self.projectsByGUID[x] for x in project.dependencies]
                        state = 'Global'
                        project = None
                    elif section is not None and project is not None:
                        if section[0] == ProjectSections.ProjectDependencies:
                            # both sides are the same.
                            project.dependencies += [
                                line.split('=')[0].strip()]
                        if section[0] == ProjectSections.SolutionItems:
                            # both sides are the same.
                            project.solutionItems += [
                                line.split('=')[0].strip()]
                elif state == 'Global':
                    if line == 'EndGlobal':
                        return
                    elif line.startswith('GlobalSection('):
                        m = REG_SECTIONPARSE.match(line)
                        if m is not None:
                            section = (m.group('name'), m.group('type'))
                    elif line == 'EndGlobalSection':
                        section = None
                    elif section is not None:
                        if section[0] == GlobalSections.NestedProjects:
                            # child = parent
                            child, parent = [x.strip()
                                             for x in line.split('=')]
                            self.projectsByGUID[parent].children.append(
                                self.projectsByGUID[child])
                        elif section[0] == GlobalSections.ProjectConfigurationPlatforms:
                            #{579B8F56-49F6-4B9D-8013-E11F69E5308C}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                            m = REG_PROJECTCONF.match(line)
                            if m is not None:
                                project_guid = m.group('project')
                                project = self.projectsByGUID[project_guid]
                                cfgA = m.group('cfgA')
                                cfgB = m.group('cfgB')
                                if cfgA not in project.configurations:
                                    project.configurations[cfgA] = collections.OrderedDict(
                                    )
                                project.configurations[cfgA][m.group(
                                    'confType')] = cfgB
                        elif section[0] == GlobalSections.SolutionConfigurationPlatforms:
                            self.configurations.append(
                                line.split('=')[0].strip())
                        elif section[0] == GlobalSections.SolutionProperties:
                            key, value = [x.strip() for x in line.split('=')]
                            #print(key, value)
                            self.properties[key] = value

    def writeline(self, f, s):
        f.write(u'{}\r\n'.format(s))

    def SaveToFile(self, filename):
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            self.writeline(f, u'Microsoft Visual Studio Solution File, Format Version {}'.format(
                self.formatVersion))
            self.writeline(f, u'# Visual Studio {}'.format(self.vsYear))
            self.writeline(
                f, u'VisualStudioVersion = {}'.format(self.vsVersion))
            self.writeline(
                f, u'MinimumVisualStudioVersion = {}'.format(self.minVSVersion))

            nestings = []
            for project in self.projects:
                for child in project.children:
                    nestings.append((child, project.guid))
                self.writeline(f, self.getProjectDeclHeader(project))
                if len(project.dependencies) > 0:
                    self.writeline(f, self.getProjectSectionStart(
                        ProjectSections.ProjectDependencies))
                    for dep in project.dependencies:
                        self.writeline(f, u'\t\t{0} = {0}'.format(dep.guid))
                    self.writeline(f, self.getProjectSectionEnd())
                if len(project.solutionItems) > 0:
                    self.writeline(f, self.getProjectSectionStart(
                        ProjectSections.SolutionItems))
                    for item in project.solutionItems:
                        self.writeline(f, u'\t\t{0} = {0}'.format(item))
                    self.writeline(f, self.getProjectSectionEnd())
                self.writeline(f, self.getProjectDeclFooter())

            self.writeline(f, u'Global')

            self.writeline(f, self.getGlobalSectionStart(
                GlobalSections.SolutionConfigurationPlatforms))
            for cfg in self.configurations:
                self.writeline(f, u'\t\t{0} = {0}'.format(cfg))
            self.writeline(f, self.getGlobalSectionEnd())

            self.writeline(f, self.getGlobalSectionStart(
                GlobalSections.ProjectConfigurationPlatforms))
            for project in self.projects:
                for projectcfg, subcfgs in project.configurations.items():
                    for subthing, slncfg in subcfgs.items():  # I have no fucking idea what these do.
                        self.writeline(f, u'\t\t{}.{}.{} = {}'.format(
                            project.guid, projectcfg, subthing, slncfg))
            self.writeline(f, self.getGlobalSectionEnd())

            if len(self.properties) > 0:
                self.writeline(f, self.getGlobalSectionStart(
                    GlobalSections.SolutionProperties))
                for k, v in self.properties.items():
                    self.writeline(f, u'\t\t{} = {}'.format(k, v))
                self.writeline(f, self.getGlobalSectionEnd())

            if len(nestings) > 0:
                self.writeline(f, self.getGlobalSectionStart(
                    GlobalSections.NestedProjects))
                for child, parent in nestings:
                    self.writeline(
                        f, u'\t\t{} = {}'.format(child.guid, parent))
                self.writeline(f, self.getGlobalSectionEnd())
            self.writeline(f, 'EndGlobal')


class VisualStudio2012Solution(Solution):
    '''
    Microsoft Visual Studio Solution File, Format Version 12.00
    # Visual Studio 2013
    VisualStudioVersion = 12.0.21005.1
    MinimumVisualStudioVersion = 10.0.40219.1
    '''

    def __init__(self):
        super().__init__()

        self.formatVersion = '12.00'
        self.vsYear = '2013'
        self.vsVersion = '12.0.21005.1'
        self.minVSVersion = '10.0.40219.1'


class VisualStudio2015Solution(Solution):
    '''
    Microsoft Visual Studio Solution File, Format Version 12.00
    # Visual Studio 14
    VisualStudioVersion = 14.0.25420.1
    MinimumVisualStudioVersion = 10.0.40219.1
    '''

    def __init__(self):
        super().__init__()

        self.formatVersion = '12.00'
        self.vsYear = '14'  # WHY
        self.vsVersion = '14.0.25420.1'
        self.minVSVersion = '10.0.40219.1'

class VisualStudio2019Solution(Solution):
    '''
    Microsoft Visual Studio Solution File, Format Version 12.00
    # Visual Studio Version 16
    VisualStudioVersion = 16.0.29102.190
    MinimumVisualStudioVersion = 10.0.40219.1
    '''

    def __init__(self):
        super().__init__()

        self.formatVersion = '12.00'
        self.vsYear = 'Version 16'  # WHY
        self.vsVersion = '16.0.29102.1'
        self.minVSVersion = '10.0.40219.1'
