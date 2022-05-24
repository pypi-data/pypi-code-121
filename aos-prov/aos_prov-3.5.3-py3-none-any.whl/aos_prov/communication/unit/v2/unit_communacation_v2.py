#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import time
from contextlib import contextmanager

import grpc
from colorama import Fore, Style
from google.protobuf import empty_pb2

from aos_prov.communication.unit.v2.generated import iamanagercommon_pb2 as iam_manager_common
from aos_prov.communication.unit.v2.generated import iamanagerprotected_pb2 as iam_manager
from aos_prov.communication.unit.v2.generated import iamanagerprotected_pb2_grpc as api_iam_manager_grpc
from aos_prov.communication.unit.v2.generated import iamanagerpublic_pb2_grpc as iam_manager_public_grpc
from aos_prov.utils.errors import BoardError, GrpcUnimplemented
from aos_prov.utils.unit_certificate import UnitCertificate

UNIT_DEFAULT_PORT = 8089


class UnitCommunicationV2:
    def __init__(self, address: str = 'localhost:8089', set_users=True):
        self._need_set_users = True

        if address is None:
            address = 'localhost:8089'
        parts = address.split(':')
        if len(parts) == 2:
            try:
                port = int(parts[1])
                if not 1 <= port <= 65535:
                    raise BoardError("Unit port is invalid")
            except ValueError:
                raise BoardError("Unit port is invalid")
        else:
            address = address + ':' + str(UNIT_DEFAULT_PORT)
        self.__unit_address = address
        print(f"Will search unit on address: {Fore.GREEN}{self.__unit_address}{Style.RESET_ALL}")

    @property
    def need_set_users(self):
        return self._need_set_users

    @need_set_users.setter
    def need_set_users(self, value):
        self._need_set_users = value

    @contextmanager
    def unit_stub(self, catch_inactive=False, wait_for_close=False):
        try:
            with grpc.insecure_channel(self.__unit_address) as channel:
                stub = api_iam_manager_grpc.IAMProtectedServiceStub(channel)
                if wait_for_close:
                    def _stop_wait(state):
                        print(str(state))
                        if state is grpc.ChannelConnectivity.SHUTDOWN:
                            channel.unsubscribe(_stop_wait)
                            print('un sss sssss')
                            return
                    channel.subscribe(_stop_wait, try_to_connect=False)
                yield stub

        except grpc.RpcError as e:
            print(e)
            if catch_inactive and \
                    not (e.code() == grpc.StatusCode.UNAVAILABLE.value and e.details() == 'Socket closed'):
                return
            elif wait_for_close and (e.code() == grpc.StatusCode.UNKNOWN.value and e.details() == 'Stream removed'):
                return
            error_text = (f"{Fore.RED}FAILED! Error occurred: {Style.RESET_ALL}"
                          f"{Fore.RED}{e.code()}: {e.details()}{Style.RESET_ALL}")
            raise BoardError(error_text)

    @contextmanager
    def unit_public_stub(self):
        try:
            with grpc.insecure_channel(self.__unit_address) as channel:
                stub = iam_manager_public_grpc.IAMPublicServiceStub(channel)
                yield stub

        except grpc.RpcError as e:
            if e.code().value == grpc.StatusCode.UNIMPLEMENTED.value:
                error_text = (f'{Fore.YELLOW}FAILED! Protocol V2 is not supported: {Style.RESET_ALL}'
                              f'{Fore.RED}{e.code()}: {e.details()}{Style.RESET_ALL}')
                raise GrpcUnimplemented(error_text)
            else:
                error_text = (f'{Fore.RED}FAILED! Error occurred: {Style.RESET_ALL}'
                              f'{Fore.RED}{e.code()}: {e.details()}{Style.RESET_ALL}')
                raise BoardError(error_text)

    def get_protocol_version(self) -> int:
        with self.unit_public_stub() as stub:
            print('Getting protocol version...')
            response = stub.GetAPIVersion(empty_pb2.Empty())
            print(f'Unit responded with version: {response.version}')
            return int(response.version)

    def get_system_info(self) -> (str, str):
        with self.unit_public_stub() as stub:
            print('Getting System Info...')
            response = stub.GetSystemInfo(empty_pb2.Empty())
            print(response)
            print('System ID: ' + response.system_id)
            print('Model name: ' + response.board_model)
            return response.system_id, response.board_model

    def clear(self, certificate_type: str) -> None:
        with self.unit_stub() as stub:
            print('Clear certificate: ' + certificate_type)
            response = stub.Clear(iam_manager.ClearRequest(type=certificate_type))
            return response

    def set_cert_owner(self, certificate_type: str, password: str) -> None:
        with self.unit_stub() as stub:
            print('Set owner: ' + certificate_type)
            response = stub.SetOwner(iam_manager.SetOwnerRequest(type=certificate_type, password=password))
            return response

    def get_cert_types(self) -> [str]:
        with self.unit_public_stub() as stub:
            print('Getting certificate types to renew')
            response = stub.GetCertTypes(empty_pb2.Empty())
            print('Will be renewed: ' + str(response.types))
            return response.types

    def create_keys(self, cert_type: str, password: str) -> UnitCertificate:
        with self.unit_stub() as stub:
            print('Generating key type:' + cert_type)
            response = stub.CreateKey(iam_manager.CreateKeyRequest(type=cert_type, password=password))
            uc = UnitCertificate()
            uc.cert_type = response.type
            uc.csr = response.csr
            return uc

    def apply_certificate(self, unit_cert: UnitCertificate):
        with self.unit_stub() as stub:
            print('Applying type:' + unit_cert.cert_type)
            stub.ApplyCert(iam_manager.ApplyCertRequest(type=unit_cert.cert_type, cert=unit_cert.certificate))

    def set_users(self, users: [str]):
        with self.unit_stub() as stub:
            print('setting users')
            stub.SetUsers(iam_manager_common.Users(users=users))

    def encrypt_disk(self, password: str):
        print('Starting disk encryption...')
        try:
            with self.unit_stub(wait_for_close=True) as stub:
                stub.EncryptDisk(iam_manager.EncryptDiskRequest(password=password))
                print('Encryption process is finished.')
        except BoardError as be:
            print('Disk encryption returned error.')
            print(be)

    def finish_provisioning(self):
        with self.unit_stub(True) as stub:
            print('Finishing provisioning')
            stub.FinishProvisioning(empty_pb2.Empty())

    def wait_for_connection(self):
        try:
            print('Sleep for 5 seconds...')
            time.sleep(5)
            print('Waiting for Unit reboot...')
            grpc.channel_ready_future(grpc.insecure_channel(self.__unit_address)).result(timeout=300)
            print('Unit is online')
        except grpc.FutureTimeoutError:
            raise BoardError('Board didnt went online')
