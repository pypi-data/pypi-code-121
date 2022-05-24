import grpc
from github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 import UserRoleClass as MDUserRoleClass
from github.com.metaprov.modelaapi.services.userroleclass.v1.userroleclass_pb2_grpc import UserRoleClassServiceStub
from github.com.metaprov.modelaapi.services.userroleclass.v1.userroleclass_pb2 import CreateUserRoleClassRequest, \
    UpdateUserRoleClassRequest, \
    DeleteUserRoleClassRequest, GetUserRoleClassRequest, ListUserRoleClassesRequest

from modela.Resource import Resource
from modela.ModelaException import ModelaException
from modela.infra.models import UserRoleClassSpec, Rule
from modela.infra.common import ResourceKind, Verb
from typing import List, Union


class UserRoleClass(Resource):
    """ User Role Classes hold rules about what actions an Account can perform on different resources. """

    def __init__(self, item: MDUserRoleClass = MDUserRoleClass(), client=None, namespace="", name="",
                 rules: List[Rule] = None):
        """
        :param client: The User Role Class client repository, which can be obtained through an instance of Modela.
        :param namespace: The target namespace of the resource.
        :param name: The name of the resource.
        :param rules: The list of rules which any Account associated with the User Role Class resource may perform.
        """
        super().__init__(item, client, namespace=namespace, name=name)

        if rules is not None:
            self.spec.Rules = rules

    @property
    def spec(self) -> UserRoleClassSpec:
        return UserRoleClassSpec().copy_from(self._object.spec).set_parent(self._object.spec)

    def default(self):
        UserRoleClassSpec().apply_config(self._object.spec)

    @property
    def rules(self):
        """ Returns the list of rules associated with the User Role Class """
        return self.spec.Rules

    def rule(self, resource: ResourceKind) -> Rule:
        """ Returns the rule for an individual resource. Returns an empty rule if the resource does not have one. """
        rule = [rule for rule in self.rules if rule.Resource == resource]
        if len(rule) > 0:
            return rule[0]
        else:
            return Rule(Resource=resource)


    def add_rule(self, rule: Rule):
        """ Adds a rule for a single resource, or merges it if a rule for the resource already exists. """
        existing_rule = [irule for irule in self.rules if irule.Resource == rule.Resource]
        if len(existing_rule) > 0:
            rule.Verbs = list(set(existing_rule[0].Verbs + rule.Verbs))
        else:
            self.spec.Rules.append(rule)

        self.update()

    def allow_verb(self, resource: ResourceKind, verb: Verb):
        """ Sets the rule for the resource to permit the specified verb """
        self.add_rule(Rule(Resource=resource, Verbs=[verb]))

    def deny_verb(self, resource: ResourceKind, verb: Verb):
        """ Sets the rule for the resource to deny the specified verb """
        rule = [rule for rule in self.rules if rule.Resource == resource]
        if len(rule) > 0:
            rule = rule[0]
            if verb.All in rule.Verbs:
                rule.Verbs = [verb.List, verb.Watch, verb.Create, verb.Update, verb.Patch, verb.Delete, verb.Get]

            try:
                rule.Verbs.remove(verb)
            except ValueError:
                pass

            self.update()

    def allow_all(self, resource: ResourceKind):
        """ Permits all operations for the specified resource """
        self.allow_verb(resource, Verb.All)

    def deny_all(self, resource: ResourceKind):
        """ Denies all operations for the specified resource """
        rule = [rule for rule in self.rules if rule.Resource == resource]
        if len(rule) > 0:
            self.rules.remove(rule[0])
            self.update()


class UserRoleClassClient:
    def __init__(self, stub, modela):
        self.modela = modela
        self.__stub: UserRoleClassServiceStub = stub

    def create(self, userroleclass: UserRoleClass) -> bool:
        request = CreateUserRoleClassRequest()
        request.UserRoleClass.CopyFrom(userroleclass.raw_message)
        try:
            response = self.__stub.CreateUserRoleClass(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def update(self, UserRoleClass: UserRoleClass) -> bool:
        request = UpdateUserRoleClassRequest()
        request.role.CopyFrom(UserRoleClass.raw_message)
        try:
            self.__stub.UpdateUserRoleClass(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def get(self, namespace: str, name: str) -> Union[UserRoleClass, bool]:
        request = GetUserRoleClassRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.GetUserRoleClass(request)
            return UserRoleClass(response.role, self)
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def delete(self, namespace: str, name: str) -> bool:
        request = DeleteUserRoleClassRequest()
        request.namespace = namespace
        request.name = name
        try:
            response = self.__stub.DeleteUserRoleClass(request)
            return True
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False

    def list(self, namespace: str) -> Union[List[UserRoleClass], bool]:
        request = ListUserRoleClassesRequest()
        request.namespace = namespace
        try:
            response = self.__stub.ListUserRoleClasses(request)
            return [UserRoleClass(item, self) for item in response.roles.items]
        except grpc.RpcError as err:
            error = err

        ModelaException.process_error(error)
        return False
