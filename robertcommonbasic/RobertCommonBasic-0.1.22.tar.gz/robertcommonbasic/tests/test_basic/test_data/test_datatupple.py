import os
import tempfile
from robertcommonbasic.basic.data.datatuple import *

class NodeType(Enum):
    big = 'big'
    little = 'little'


class NodeAttribute(DataTuple):
    name: str
    data_tuple: DataTuple


def is_dict_equal(d1: dict, d2: dict):
    d3 = {k: d1[k] for k in d1 if k in d2 and d1[k] == d2[k]}
    return len(d3) == len(d1) == len(d2)


def is_dict_list_equal(l1: list, l2: list):
    assert len(l1) == len(l2)
    for d1, d2 in zip(l1, l2):
        assert is_dict_equal(d1, d2)


multi_lang_str = multi_lang(str)
multi_lang_attribute = multi_lang(NodeAttribute)


class Node(DataTuple):
    id: int
    __name__: Optional[str]
    type: NodeType
    template_ids: List[ObjectId]
    update_time: datetime = field(
        default_factory=lambda: datetime(2020, 1, 1),
        metadata={'time_format': '%Y-%m-%d %H:%M:%S'},
        tags=['test'])
    attributes: List[NodeAttribute]
    attribute: NodeAttribute = field(tags=['test'])
    is_group: bool = field(default=False)
    health_rate: float = field(
        metadata={'data_range': {
            'min': 0,
            'max': 10.1
        }})
    any_field: Any
    json_field: dict
    default_int: int
    multi_lang_str: multi_lang_str
    multi_lang_attribute: multi_lang_attribute

def test_datatuples_to_csv():
    nodes = [
        Node(
            id=1,
            name=11111,
            type='big',
            template_ids=[
                '592f8136833c977d4d2d74f1', '592f8136833c977d4d2d74f4'
            ],
            update_time='2020-09-01 00:12:13',
            attributes=[NodeAttribute(name='A_Attr')],
            attribute='''{
            "name": "A_Attr"
        }''',
            is_group=False,
            health_rate=2,
            json_field={
                's': 'string',
                1: 12341324
            },
            multi_lang_str={
                'en': 1234,
                'zh': 'zh_str',
                'jp': 'jp_str'
            },
            multi_lang_attribute={'en': NodeAttribute(name='en_attr')},
        ),
        Node(
            id=2,
            name=2222,
            type='little',
            template_ids=[],
            update_time='2020-09-01 00:12:14',
            attributes=[NodeAttribute(name='B_Attr')],
            attribute='''{
            "name": "B_Attr"
        }''',
            is_group=False,
            health_rate=2,
            json_field={
                's': 'string',
                1: 12341324
            },
            multi_lang_str={
                'en': 1234,
                'jp': 'jp_str'
            },
            multi_lang_attribute={'zh': NodeAttribute(name='zh_attr')},
        )
    ]
    tempdir = tempfile.TemporaryDirectory()
    expect = [{
        'id':
        1,
        'name':
        '11111',
        'type':
        'big',
        'template_ids': [
            ObjectId('592f8136833c977d4d2d74f1'),
            ObjectId('592f8136833c977d4d2d74f4')
        ],
        'update_time':
        datetime(2020, 9, 1, 0, 12, 13),
        'attributes': [{
            'name': 'A_Attr'
        }],
        'attribute': {
            'name': 'A_Attr'
        },
        'is_group':
        False,
        'health_rate':
        2.0,
        'json_field': {
            's': 'string',
            1: 12341324
        },
        'multi_lang_str': {
            'en': '1234',
            'zh': 'zh_str'
        },
        'multi_lang_attribute': {
            'en': {
                'name': 'en_attr'
            }
        }
    }, {
        'id': 2,
        'name': '2222',
        'type': 'little',
        'template_ids': [],
        'update_time': datetime(2020, 9, 1, 0, 12, 14),
        'attributes': [{
            'name': 'B_Attr'
        }],
        'attribute': {
            'name': 'B_Attr'
        },
        'is_group': False,
        'health_rate': 2.0,
        'json_field': {
            's': 'string',
            1: 12341324
        },
        'multi_lang_str': {
            'en': '1234'
        },
        'multi_lang_attribute': {
            'zh': {
                'name': 'zh_attr'
            }
        }
    }]
    tmp_file_path = os.path.join(tempdir.name, 'test.csv')
    with open(tmp_file_path, 'w') as tmp_file:
        datatuples_to_sheet(nodes,
                            io=tmp_file,
                            expand_lang=False,
                            sheet_type=SheetType.csv)
    datatuples = datatuples_read_sheet(Node,
                                       path=tmp_file.name,
                                       sheet_type=SheetType.csv)
    actual = datatuples_to_bson(datatuples)
    #is_dict_list_equal(actual, expect)
    df = pd.read_csv(tmp_file_path)

    os.unlink(tmp_file_path)
    tmp_file_path = os.path.join(tempdir.name, 'test.xlsx')
    datatuples_to_sheet(nodes,
                        path=tmp_file_path,
                        sheet_type=SheetType.excel,
                        expand_lang=True)
    datatuples = datatuples_read_sheet(Node,
                                       path=tmp_file_path,
                                       sheet_type=SheetType.excel,
                                       expand_lang=True)
    df = pd.read_excel(tmp_file_path, engine='openpyxl')
    assert list(df.columns) == [
        'id', 'name', 'type', 'template_ids', 'update_time', 'attributes',
        'attribute', 'is_group', 'health_rate', 'json_field',
        'multi_lang_str.en', 'multi_lang_str.zh', 'multi_lang_attribute.en',
        'multi_lang_attribute.zh', 'any_field', 'default_int'
    ]
    actual = datatuples_to_bson(datatuples)
    is_dict_list_equal(actual, expect)
    os.unlink(tmp_file_path)
    tempdir.cleanup()

test_datatuples_to_csv()