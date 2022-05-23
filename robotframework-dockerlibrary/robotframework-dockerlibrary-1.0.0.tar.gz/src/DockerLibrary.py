import re
import subprocess
from typing import AnyStr, Dict, List, Match, Optional, Union

from src.Utils import Const, DotDictionary, Utils


class DockerLibrary:
    
    def create_multiple_containers(self, n_containers: int, image: str) -> \
        List[str]:
        containers_id: List[str] = list()
        for _ in range(n_containers):
            con_id = str(self.docker('run', '-dt', image).stdout)
            if con_id:
                containers_id.append(Utils.parse_containers_ids(con_id)[0])
        return containers_id
    
    def docker_command_for_all(self, containers_ids: Union[List[str], str], 
        parse_to_dotd: bool, *args: Optional[str]) -> Dict[str, Union[DotDictionary, str]]:
        result: Dict[str, Union[List[DotDictionary], DotDictionary, str]] = dict()
        ids = containers_ids
        if isinstance(containers_ids, str):
            ids = Utils.parse_containers_ids(containers_ids)
        for con_id in ids:
            result[con_id] = self.parse_docker_response(
                self.docker(*args, con_id).stdout, parse_to_dotd)
        return result
    
    def docker_in_docker(self, 
                         host_image: str, 
                         dind_image: str, 
                         n_dind: int, 
                         port: Optional[str] = None) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = dict()
        con_id: Optional[str] = None
        if host_image.lower() in Const.HOST_IMAGES:
            self.docker('build', '-t', host_image + "-dind", Const.HOST_IMAGES[host_image])
            if port:
                con_id = str(self.docker('run', '-dt', '-p', port, '-v',
                    '/var/run/docker.sock:/var/run/docker.sock', host_image + "-dind").stdout)
            else:
                con_id = str(self.docker('run', '-dt', '-v',
                    '/var/run/docker.sock:/var/run/docker.sock', host_image + "-dind").stdout)
        if con_id:
            host_id = Utils.parse_containers_ids(con_id)[0]
            dind_ids: List[str] = list()
            for _ in range(n_dind):
                dind_ids.append(Utils.parse_containers_ids(str(
                    self.docker('exec', host_id, 'docker', 'run', '-dt', dind_image).stdout))[0])
            result[host_id] = self.parse_docker_response(str(dind_ids), False)
        return result
    
    @staticmethod
    def docker(*args: Optional[str]) -> subprocess.CompletedProcess:
        return subprocess.run(['docker'] + list(args), stdout=subprocess.PIPE)

    def get_containers_ids(self) -> List[str]:
        text = str(self.docker('ps', '-a', '-q').stdout)
        return Utils.parse_containers_ids(text)

    def parse_docker_response(self, text: str, parse_to_dotd: bool) -> \
        Union[List[DotDictionary], DotDictionary, str]:
        decoded_text: str = str(text)
        m: Optional[Match[AnyStr]] = Const.DECODE_RE.match(decoded_text)
        if m:
            decoded_text: Optional[str] = m.groupdict().get("values")
        clean_text = re.sub(r'\s+|\\n+', '', decoded_text)
        if parse_to_dotd:
            return Utils.parse_docker_response_helper(clean_text)
        return clean_text
