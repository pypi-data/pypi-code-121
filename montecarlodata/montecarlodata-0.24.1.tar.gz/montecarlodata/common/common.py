import base64
import ipaddress
import json
import pkgutil
import secrets
from collections.abc import Mapping
from functools import wraps
from typing import Optional, Dict, List, Any, io, Iterator

from box import Box
from jinja2 import Template
from pycarlo.core import Client, Session

from montecarlodata.config import Config


def normalize_gql(field: str) -> Optional[str]:
    if field:
        return field.replace('_', '-').lower()


def read_as_base64(path: str) -> bytes:
    with open(path, 'rb') as fp:
        return base64.b64encode(fp.read())


def read_as_json(path: str) -> Dict:
    with open(path) as file:
        return json.load(file)


def read_as_json_string(path: str) -> str:
    """"Read and validate JSON file"""
    return json.dumps(read_as_json(path))


def struct_match(s1: Dict, s2: Dict) -> bool:
    return json.dumps(s1, sort_keys=True) == json.dumps(s2, sort_keys=True)


def boxify(use_snakes: Optional[bool] = False,
           default_box_attr: Optional[Any] = object(),
           default_box: Optional[bool] = False):
    """
    Convenience decorator to convert a dict into Box for ease of use.

    Set `use_snakes` to convert camelCase to snake_case. Use `default_box_attr` to set a default value.
    """

    def _boxify(func):
        @wraps(func)
        def _impl(self, *args, **kwargs):
            dict_ = func(self, *args, **kwargs)
            if dict_ and isinstance(dict_, Mapping):
                return Box(
                    dict_,
                    camel_killer_box=use_snakes,
                    default_box_attr=default_box_attr,
                    default_box=default_box
                )
            return dict_

        return _impl

    return _boxify


def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def is_overlap(r1: str, r2: str) -> bool:
    """Check if two CIDR ranges overlap"""
    r1 = ipaddress.ip_network(r1)
    r2 = ipaddress.ip_network(r2)
    return r1.overlaps(r2) or r2.overlaps(r1)


def create_mc_client(ctx: Dict) -> Client:
    config: Config = ctx['config']
    mc_client = Client(
        session=Session(
            mcd_id=config.mcd_id,
            mcd_token=config.mcd_token
        )
    )
    return mc_client


def read_files(files: List[io]) -> Iterator[str]:
    """Read a list of files"""
    for fp in files:
        yield fp.read()


def render_dumped_json(path: str, **kwargs) -> str:
    """Render and dump as formatted JSON"""
    return json.dumps(json.loads(render(path, **kwargs)), indent=4, sort_keys=True)


def render(path: str, **kwargs) -> str:
    """Load file from path and inject kwargs."""
    template = Template(pkgutil.get_data(__name__, path).decode('utf-8'))
    return template.render(**kwargs)


def generate_token(length: Optional[int] = 16) -> str:
    """Generate a random url safe token"""
    return secrets.token_urlsafe(length)
