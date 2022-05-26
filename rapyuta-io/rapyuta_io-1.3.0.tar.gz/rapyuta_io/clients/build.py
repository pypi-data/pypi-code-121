from __future__ import absolute_import
import enum
import time

from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils import ObjDict, to_objdict
from rapyuta_io.clients.package import ROSDistro
from rapyuta_io.clients.device_manager import DeviceArch
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils import RestClient, RetriesExhausted
from rapyuta_io.utils.error import BuildFailed
from rapyuta_io.clients.buildoperation import BuildOperation, BuildOperationInfo
from rapyuta_io.utils.error import BuildOperationFailed
from rapyuta_io.utils.partials import PartialMixin
from rapyuta_io.utils.pollers import RefreshPollerMixin
import six
from six.moves import range


class SimulationOptions(ObjDict):
    """
    Simulation Options represents whether simulation is required at the time of building package

    :ivar simulation: whether simulation is required (bool).
    """
    def __init__(self, simulation):
        self.validate(simulation)
        self.simulation = simulation
        super(ObjDict, self).__init__()

    @staticmethod
    def validate(simulation):
        if not isinstance(simulation, bool):
            raise InvalidParameterException('simulation must be a boolean')


class BuildOptions(ObjDict):
    """
    BuildOptions represent Build Options.

    :ivar catkinOptions: represents list of catkin options :py:class:`~rapyuta_io.clients.build.CatkinOption`.

    """
    def __init__(self, catkinOptions):
        self.validate(catkinOptions)
        self.catkinOptions = catkinOptions
        super(ObjDict, self).__init__()

    @staticmethod
    def validate(catkinOptions):
        if not isinstance(catkinOptions, list):
            raise InvalidParameterException('catkinOptions must be an instance of list')
        for opt in catkinOptions:
            if not isinstance(opt, CatkinOption):
                raise InvalidParameterException('Every catkinOption must be an instance of '
                                                'rapyuta_io.clients.build.CatkinOption')


class CatkinOption(ObjDict):
    """
    CatkinOption represents Catkin Options

    :ivar rosPkgs: Represents ROS packages to be included for build.
    :ivar cmakeArgs: Represents cmakeArgs to be used in the build.
    :ivar makeArgs: Represents makeArgs to be used in the build.
    :ivar blacklist: Used if you want to avoid build certain packages in your build.
    :ivar catkinMakeArgs: Represents catkinMakeArgs to be used in the build.

    """
    def __init__(self, rosPkgs=None, cmakeArgs=None, makeArgs=None, blacklist=None, catkinMakeArgs=None):
        self.validate(rosPkgs, cmakeArgs, makeArgs, blacklist, catkinMakeArgs)
        self.rosPkgs = rosPkgs
        self.cmakeArgs = cmakeArgs
        self.makeArgs = makeArgs
        self.blacklist = blacklist
        self.catkinMakeArgs = catkinMakeArgs
        super(ObjDict, self).__init__()

    @staticmethod
    def validate(rosPkgs, cmakeArgs, makeArgs, blacklist, catkinMakeArgs):
        if rosPkgs and not isinstance(rosPkgs, six.string_types):
            raise InvalidParameterException('rosPkgs must be of string type')

        if cmakeArgs and not isinstance(cmakeArgs, six.string_types):
            raise InvalidParameterException('cmakeArgs must be of string type')

        if makeArgs and not isinstance(makeArgs, six.string_types):
            raise InvalidParameterException('makeArgs must be of string type')

        if blacklist and not isinstance(blacklist, six.string_types):
            raise InvalidParameterException('blacklist must be of string type')

        if catkinMakeArgs and not isinstance(catkinMakeArgs, six.string_types):
            raise InvalidParameterException('catkinMakeArgs must be of string type')


class GithubWebhook(ObjDict):
    """
    Github Webhook to be triggered on build completion

    :ivar workflowName: Represents name of the github dispatch workflow file.
    :ivar accessToken: Represents github access token

    """
    WebhookType = "githubWorkflow"

    def __init__(self, workflowName, accessToken):
        self.validate(workflowName, accessToken)
        self.webhookType = GithubWebhook.WebhookType
        self.workflowName = workflowName
        self.accessToken = accessToken

    @staticmethod
    def validate(workflowName, accessToken):

        if not workflowName or not isinstance(workflowName, six.string_types):
            raise InvalidParameterException('workflowName must be present and should be of string type')

        if not accessToken or not isinstance(accessToken, six.string_types):
            raise InvalidParameterException('accessToken must be present and should be of string type')


class Build(PartialMixin, RefreshPollerMixin, ObjDict):

    """
    Build represents the main class whose instance will be used to perform various operations like create, get, update,
    delete, trigger and rollback

    :param buildName: name of build
    :type buildName: str
    :param strategyType: Strategy type used for the build
    :type strategyType: Union[:py:class:`~rapyuta_io.clients.build.StrategyType`, str]
    :param repository: Git repository to be used for building docker image while deploying package.
    :type repository: str
    :param architecture: Architecture required for using the build
    :type architecture: Union[:py:class:`~rapyuta_io.clients.device_manager.DeviceArch`, str]
    :param rosDistro: ROS distro used by the build
    :type rosDistro: Union[:py:class:`~rapyuta_io.clients.package.ROSDistro`, str]
    :param isRos: Whether the build support ros components
    :type isRos: bool
    :param contextDir: context dir to be used in the build
    :type contextDir: str
    :param dockerFilePath: Represents Docker file path
    :type dockerFilePath: str
    :param secret: Represents secret for a private git repository
    :type secret: str
    :param dockerPullSecret: GUID of the docker secret for a private base image in Dockerfile
    :type dockerPullSecret: str
    :param dockerPushSecret: GUID of the docker secret for pushing the image to an external registry.
    :type dockerPushSecret: str
    :param dockerPushRepository: An external docker repository where Build will push the image. For example 'docker.io/user/example'
    :type dockerPushRepository: str
    :param simulationOptions: Represents simulation options used by the build
    :type simulationOptions: :py:class:`~rapyuta_io.clients.build.SimulationOptions`
    :param buildOptions: Represents build options used by the build
    :type buildOptions: :py:class:`~rapyuta_io.clients.build.BuildOptions`
    :param branch: Represents branch corresponding to the repository used by the build
    :type branch: str
    :param triggerName: Represents trigger name of the build
    :type triggerName: str
    :param tagName: Represents tag name of the build
    :type tagName: str
    :param buildWebhooks: Represents webhooks to be triggered on build completion
    :type buildWebhooks: list(:py:class:`~rapyuta_io.clients.build.GithubWebhook`)
    """
    def __init__(self, buildName, strategyType, repository, architecture, rosDistro='',
                 isRos=False,  contextDir='', dockerFilePath='', secret='',
                 dockerPullSecret='', dockerPushSecret='', dockerPushRepository='',
                 simulationOptions=None, buildOptions=None, branch='', triggerName='', tagName='', buildWebhooks=None):

        self.validate(buildName, strategyType, repository, architecture, rosDistro, isRos,
                      contextDir, dockerFilePath, secret, dockerPullSecret, dockerPushSecret,
                      dockerPushRepository, simulationOptions, buildOptions, branch, triggerName, tagName, buildWebhooks)

        if not strategyType or strategyType not in list(StrategyType.__members__.values()):
            raise InvalidParameterException('StrategyType must be one of rapyuta_io.clients.package.StrategyType')

        if not architecture or architecture not in list(DeviceArch.__members__.values()):
            raise InvalidParameterException('architecture must be one of rapyuta_io.clients.device_manager.DeviceArch')

        if rosDistro != '' and rosDistro not in list(ROSDistro.__members__.values()):
            raise InvalidParameterException('rosDistro  must be one of rapyuta_io.clients.package.ROSDistro')

        self.buildName = buildName
        self.secret = secret
        self.dockerPullSecret = dockerPullSecret
        self.dockerPushSecret = dockerPushSecret
        self.dockerPushRepository = dockerPushRepository
        self.triggerName = triggerName
        self.tagName = tagName
        self.buildInfo = ObjDict(
            repository=repository,
            branch=branch,
            strategyType=strategyType,
            dockerFilePath=dockerFilePath,
            contextDir=contextDir,
            architecture=architecture,
            isRos=isRos,
            rosDistro=rosDistro
        )
        self.buildInfo.simulationOptions = simulationOptions
        self.buildInfo.buildOptions = buildOptions
        self.buildWebhooks = buildWebhooks

        super(ObjDict, self).__init__()

    @staticmethod
    def validate(buildName, strategyType, repository, architecture, rosDistro, isRos,
                 contextDir, dockerFilePath, secret, dockerPullSecret, dockerPushSecret,
                 dockerPushRepository, simulationOptions, buildOptions, branch, triggerName, tagName, buildWebhooks):

        if not buildName or not isinstance(buildName, six.string_types):
            raise InvalidParameterException('buildName must be a non-empty string')

        if not strategyType or strategyType not in list(StrategyType.__members__.values()):
            raise InvalidParameterException('StrategyType must be one of rapyuta_io.clients.package.StrategyType')

        if not repository or not isinstance(repository, six.string_types):
            raise InvalidParameterException('repository must be a valid non-empty string')

        if branch != '' and not isinstance(branch, six.string_types):
            raise InvalidParameterException('branch must be a valid non-empty string')

        if not architecture or architecture not in list(DeviceArch.__members__.values()):
            raise InvalidParameterException('Architecture must be one of rapyuta_io.clients.device_manager.DeviceArch')

        if not isinstance(isRos, bool):
            raise InvalidParameterException('isRos must be of bool type')

        if not isRos and rosDistro != '':
            raise InvalidParameterException('rosDistro must not be set if isRos is False')
        elif isRos and rosDistro not in list(ROSDistro.__members__.values()):
            raise InvalidParameterException('rosDistro must be one of rapyuta_io.clients.package.ROSDistro')

        if not isRos and (buildOptions or simulationOptions):
            raise InvalidParameterException('isRos must be true for passing simulationOptions or buildOptions')

        if simulationOptions is not None and not isinstance(simulationOptions, SimulationOptions):
            raise InvalidParameterException('simulationOptions must be of rapyuta_io.clients.build.SimulationOptions')

        if buildOptions is not None and not isinstance(buildOptions, BuildOptions):
            raise InvalidParameterException('buildOptions must be of rapyuta_io.clients.build.BuildOptions')

        if not isinstance(contextDir, six.string_types):
            raise InvalidParameterException('contextDir must be a string')

        if strategyType == StrategyType.SOURCE and dockerFilePath:
            raise InvalidParameterException('cannot use dockerFilePath for source strategyType')

        if not isinstance(dockerFilePath, six.string_types):
            raise InvalidParameterException('dockerFilePath must be a non-empty string')

        if not isinstance(secret, six.string_types):
            raise InvalidParameterException('secret must be a string')

        if not isinstance(dockerPullSecret, six.string_types):
            raise InvalidParameterException('dockerPullSecret must be a string')

        if not isinstance(dockerPushSecret, six.string_types):
            raise InvalidParameterException('dockerPushSecret must be a string')

        if not isinstance(dockerPushRepository, six.string_types):
            raise InvalidParameterException('dockerPushRepository must be a string')

        if (dockerPushRepository == '' and dockerPushSecret != '') or (dockerPushRepository != '' and dockerPushSecret == ''):
            raise InvalidParameterException('both dockerPushRepository and dockerPushSecret must be present')

        if not isinstance(triggerName, six.string_types):
            raise InvalidParameterException('triggerName must be a non-empty string')

        if not isinstance(tagName, six.string_types):
            raise InvalidParameterException('tagName must be a non-empty string')

        if dockerPushSecret == '' and tagName != '':
            raise InvalidParameterException('cannot use tagName without dockerPushSecret')

        if buildWebhooks is not None and (not isinstance(buildWebhooks, list) or not all(isinstance(webhook, GithubWebhook) for webhook in buildWebhooks)):
            raise InvalidParameterException('buildWebhooks must be a list of rapyuta_io.clients.build.GithubWebhook')


    @classmethod
    def _deserialize(cls, data, obj=None):
        if obj:  # refresh existing object
            for key, value in six.iteritems(data):
                if key != 'buildInfo':  # preserve class objects like enums & options
                    setattr(obj, key, value)
            return obj

        obj = cls.__new__(cls)
        for key, value in six.iteritems(data):
            setattr(obj, key, value)
        obj.buildInfo['strategyType'] = StrategyType(obj.buildInfo['strategyType'])
        obj.buildInfo['architecture'] = DeviceArch(obj.buildInfo['architecture'])
        if obj.buildInfo.get('rosDistro'):
            obj.buildInfo['rosDistro'] = ROSDistro(obj.buildInfo.get('rosDistro'))
        obj.buildInfo = to_objdict(obj.buildInfo)     # Not allowing buildOptions, simulationOptions to get recursively
                                                      # converted into objdict
        buildOptions = getattr(obj.buildInfo, 'buildOptions', None)
        buildOptsObj = None
        if buildOptions:
            buildOptsObj = BuildOptions.__new__(BuildOptions)
            catkinOptObjs = []
            for opt in buildOptions.get('catkinOptions', []):
                catkinOptObj = CatkinOption.__new__(CatkinOption)
                catkinOptObj.update(**opt)
                catkinOptObjs.append(catkinOptObj)
            buildOptsObj.catkinOptions = catkinOptObjs
        obj.buildInfo.buildOptions = buildOptsObj
        simulationOptions = getattr(obj.buildInfo, 'simulationOptions', None)
        simOptsObj =None
        if simulationOptions:
            simOptsObj = SimulationOptions.__new__(SimulationOptions)
            simOptsObj.update(**simulationOptions)
        obj.buildInfo.simulationOptions = simOptsObj
        # populating default values in case of missing fields
        fields_inside_buildinfo = ['repository', 'branch', 'dockerFilePath', 'contextDir', 'rosDistro']
        fields_outside_buildinfo = ['secret', 'dockerPullSecret', 'dockerPushSecret', 'dockerPushRepository']
        for key in fields_inside_buildinfo:
            setattr(obj.buildInfo, key, getattr(obj.buildInfo, key, ''))
        for key in fields_outside_buildinfo:
            setattr(obj, key, getattr(obj, key, ''))
        return obj

    def _serialize(self):
        build = {
            'buildName': self.buildName,
            'strategyType': self.buildInfo.strategyType,
            'repository': self.buildInfo.repository,
            'architecture': self.buildInfo.architecture,
            'isRos': self.buildInfo.isRos,
        }
        if self.secret != '':
            build['secret'] = self.secret

        if self.dockerPullSecret != '':
            build['dockerPullSecrets'] = [self.dockerPullSecret]

        if self.dockerPushSecret != '':
            build['dockerPushSecret'] = self.dockerPushSecret

        if self.dockerPushRepository != '':
            build['dockerPushRepository'] = self.dockerPushRepository

        if hasattr(self, 'triggerName') and self.triggerName != '':
            build['triggerName'] = self.triggerName

        if hasattr(self, 'tagName') and self.tagName != '':
            build['tagName'] = self.tagName

        if self.buildInfo.get('rosDistro'):
            build['rosDistro'] = self.buildInfo.get('rosDistro')

        if self.buildInfo.get('simulationOptions'):
            build['simulationOptions'] = self.buildInfo.get('simulationOptions')

        if self.buildInfo.get('buildOptions'):
            build['buildOptions'] = self.buildInfo.get('buildOptions')

        if self.buildInfo.get('dockerFilePath'):
            build['dockerFilePath'] = self.buildInfo.get('dockerFilePath')

        if self.buildInfo.get('contextDir'):
            build['contextDir'] = self.buildInfo.get('contextDir')

        if self.buildInfo.get('branch'):
            build['branch'] = self.buildInfo.get('branch')

        if hasattr(self, 'buildWebhooks') and self.buildWebhooks is not None:
            build['buildWebhooks'] = self.buildWebhooks

        return build

    def refresh(self):

        """
        Fetches the updated resource from the server, and adds/updates object attributes based on it.

        :raises: :py:class:`~utils.error.APIError`: If the api returns an error, the status code is
            anything other than 200/201
        """
        url = self._host + '/build/{}'.format(self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        response_data = get_api_response_data(response, parse_full=True)
        self._deserialize(response_data, obj=self)
        self.is_partial = False

    def save(self):

        """
        Save the build after updating attributes

        Following are the attributes that can be updated

        * build.buildInfo.repository
        * build.buildInfo.branch
        * build.buildInfo.dockerFilePath
        * build.buildInfo.contextDir
        * build.buildInfo.buildOptions
        * build.secret
        * build.dockerPullSecret
        * build.dockerPushRepository

        Following example demonstrates how to save a build:

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid')
            >>> build.buildInfo.branch = 'master'
            >>> build.save()
        """

        self.validate(self.buildName,
                      self.buildInfo.strategyType,
                      self.buildInfo.repository,
                      self.buildInfo.architecture,
                      self.buildInfo.rosDistro,
                      self.buildInfo.isRos,
                      self.buildInfo.contextDir,
                      self.buildInfo.dockerFilePath,
                      self.secret,
                      self.dockerPullSecret,
                      self.dockerPushSecret,
                      self.dockerPushRepository,
                      self.buildInfo.simulationOptions,
                      self.buildInfo.buildOptions,
                      self.buildInfo.branch,
                      '',
                      '',
                      None
                      )
        url = self._host + '/build/{}'.format(self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=self._serialize())
        get_api_response_data(response, parse_full=True)

    def delete(self):

        """
        Delete the build using the build object.
        :raises: :py:class:`ForbiddenError`: Returned in case of status code 403

        Following example demonstrates how to delete a build using build object:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import ForbiddenError
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid')
            >>> try:
            ...     build.delete()
            ... except ForbiddenError as e:
            ...     print e

        """
        url = self._host + '/build/{}'.format(self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        get_api_response_data(response, parse_full=True)

    def trigger(self, triggerName=None, tagName=None):

        """
        Trigger a new build request for a build using build object.

        :raises: :py:class:`BuildOperationFailed`: Returned in case trigger build fails

        Following example demonstrates how to trigger a new build request using build object:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import BuildOperationFailed
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid')
            >>> try:
            ...     build.trigger()
            ... except BuildOperationFailed as e:
            ...     print e

        """
        url = self._host + '/build/operation/trigger'
        headers = create_auth_header(self._auth_token, self._project)
        build_operation_info = [BuildOperationInfo(self.guid, triggerName=triggerName, tagName=tagName)]
        request = BuildOperation(buildOperationInfo=build_operation_info)
        trigger_response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=request)
        response_data = get_api_response_data(trigger_response, parse_full=True)
        if not response_data['buildOperationResponse'][0]['success']:
            raise BuildOperationFailed(response_data['buildOperationResponse'][0]['error'])
        self['buildGeneration'] = response_data['buildOperationResponse'][0]['buildGenerationNumber']

    def rollback(self, buildGenerationNumber):

        """
        Rollback a build using build object.

        :param buildGenerationNumber: build generation number used for rollback.
        :type buildGenerationNumber: int
        :raises: :py:class:`BuildOperationFailed`: Returned in case rollback build fails.
        :raises: :py:class:`InvalidParameterException`

        Following example demonstrates how to rollback a build using build object:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import BuildOperationFailed
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid')
            >>> try:
            ...     build.rollback(1)
            ... except BuildOperationFailed as e:
            ...     print e

        """
        if not isinstance(buildGenerationNumber, int) or buildGenerationNumber <= 0:
            msg = 'build generation number must be an integer and greater than 0'
            raise InvalidParameterException(msg)
        url = self._host + '/build/operation/rollback'
        headers = create_auth_header(self._auth_token, self._project)
        build_operation_info = [BuildOperationInfo(self.guid, buildGenerationNumber)]
        request = BuildOperation(buildOperationInfo=build_operation_info)
        rollback_response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=request)
        response_data = get_api_response_data(rollback_response, parse_full=True)
        if not response_data['buildOperationResponse'][0]['success']:
            raise BuildOperationFailed(response_data['buildOperationResponse'][0]['error'])
        self['buildGeneration'] = buildGenerationNumber

    def poll_build_till_ready(self, retry_count=120, sleep_interval=5):
        """
        Polls the build till its status changes from BuildInProgress to Complete/BuildFailed.

        :param retry_count: Number of retries.
        :type retry_count: int
        :param sleep_interval: Sleep seconds between retries.
        :type sleep_interval: int
        :raises: :py:class:`BuildFailed`: If status becomes BuildFailed.
        :raises: :py:class:`RetriesExhausted`: If the number of polling retries exhausted before the object was ready.

        Following example demonstrates how to poll a newly created build using build object:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import BuildFailed, RetriesExhausted
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = Build('test-build', 'Source', 'repository', 'amd64', 'melodic', isRos=True)
            >>> build = client.create_build(build)
            >>> try:
            ...     build.poll_build_till_ready()
            ... except BuildFailed:
            ...     print 'Build Failed'
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again ?'

        """
        self.poll_till_ready(retry_count, sleep_interval)

    def is_ready(self):
        if self.status == BuildStatus.BUILD_FAILED:
            raise BuildFailed()
        return self.status == BuildStatus.COMPLETE


class BuildStatus(str, enum.Enum):
    """
    Enumeration variables for build status

    Build status can be any of the following types \n

    BuildStatus.BUILD_IN_PROGRESS \n
    BuildStatus.COMPLETE \n
    BuildStatus.BUILD_FAILED \n

    """

    def __str__(self):
        return str(self.value)

    BUILD_IN_PROGRESS = 'BuildInProgress'
    COMPLETE = 'Complete'
    BUILD_FAILED = 'BuildFailed'

    @staticmethod
    def validate(statuses):
        if not isinstance(statuses, list):
            raise InvalidParameterException('statuses must be an instance of list')
        for status in statuses:
            if status not in list(BuildStatus.__members__.values()):
                raise InvalidParameterException('status must be of rapyuta_io.clients.build.BuildStatus')


class StrategyType(str, enum.Enum):
    """
    Enumeration variables for Strategy Types.

    Strategy Type can be any of the following types \n

    StrategyType.SOURCE \n
    StrategyType.DOCKER \n
    """

    def __str__(self):
        return str(self.value)

    SOURCE = 'Source'
    DOCKER = 'Docker'