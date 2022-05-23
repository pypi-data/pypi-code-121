# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome5_from_dict(json.loads(json_string))

from typing import Any, List, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


class Bic:
    code: str
    selected: bool

    def __init__(self, code: str, selected: bool) -> None:
        self.code = code
        self.selected = selected

    @staticmethod
    def from_dict(obj: Any) -> 'Bic':
        assert isinstance(obj, dict)
        code = from_str(obj.get("code"))
        selected = from_bool(obj.get("selected"))
        return Bic(code, selected)

    def to_dict(self) -> dict:
        result: dict = {}
        result["code"] = from_str(self.code)
        result["selected"] = from_bool(self.selected)
        return result


class PanelConfig:
    bic: List[Bic]

    def __init__(self, bic: List[Bic]) -> None:
        self.bic = bic

    @staticmethod
    def from_dict(obj: Any) -> 'PanelConfig':
        assert isinstance(obj, dict)
        bic = from_list(Bic.from_dict, obj.get("bic"))
        return PanelConfig(bic)

    def to_dict(self) -> dict:
        result: dict = {}
        result["bic"] = from_list(lambda x: to_class(Bic, x), self.bic)
        return result


class SchemaInfo:
    schema_ext: str
    schema: str

    def __init__(self, schema_ext: str, schema: str) -> None:
        self.schema_ext = schema_ext
        self.schema = schema

    @staticmethod
    def from_dict(obj: Any) -> 'SchemaInfo':
        assert isinstance(obj, dict)
        schema_ext = from_str(obj.get("schemaExt"))
        schema = from_str(obj.get("schema"))
        return SchemaInfo(schema_ext, schema)

    def to_dict(self) -> dict:
        result: dict = {}
        result["schemaExt"] = from_str(self.schema_ext)
        result["schema"] = from_str(self.schema)
        return result


class DisplayMsgs:
    dp_switch_led: str
    quickop_dp_switch_led: str
    dp_switch_led_off: str
    quickop_dp_bright_value_unit: str
    quickop_dp_switch_led_off: str
    quickop_dp_bright_value: str
    dp_switch_led_on: str
    quickop_dp_switch_led_on: str

    def __init__(self, dp_switch_led: str, quickop_dp_switch_led: str, dp_switch_led_off: str, quickop_dp_bright_value_unit: str, quickop_dp_switch_led_off: str, quickop_dp_bright_value: str, dp_switch_led_on: str, quickop_dp_switch_led_on: str) -> None:
        self.dp_switch_led = dp_switch_led
        self.quickop_dp_switch_led = quickop_dp_switch_led
        self.dp_switch_led_off = dp_switch_led_off
        self.quickop_dp_bright_value_unit = quickop_dp_bright_value_unit
        self.quickop_dp_switch_led_off = quickop_dp_switch_led_off
        self.quickop_dp_bright_value = quickop_dp_bright_value
        self.dp_switch_led_on = dp_switch_led_on
        self.quickop_dp_switch_led_on = quickop_dp_switch_led_on

    @staticmethod
    def from_dict(obj: Any) -> 'DisplayMsgs':
        assert isinstance(obj, dict)
        dp_switch_led = from_str(obj.get("dp_switch_led"))
        quickop_dp_switch_led = from_str(obj.get("quickop_dp_switch_led"))
        dp_switch_led_off = from_str(obj.get("dp_switch_led_off"))
        quickop_dp_bright_value_unit = from_str(obj.get("quickop_dp_bright_value_unit"))
        quickop_dp_switch_led_off = from_str(obj.get("quickop_dp_switch_led_off"))
        quickop_dp_bright_value = from_str(obj.get("quickop_dp_bright_value"))
        dp_switch_led_on = from_str(obj.get("dp_switch_led_on"))
        quickop_dp_switch_led_on = from_str(obj.get("quickop_dp_switch_led_on"))
        return DisplayMsgs(dp_switch_led, quickop_dp_switch_led, dp_switch_led_off, quickop_dp_bright_value_unit, quickop_dp_switch_led_off, quickop_dp_bright_value, dp_switch_led_on, quickop_dp_switch_led_on)

    def to_dict(self) -> dict:
        result: dict = {}
        result["dp_switch_led"] = from_str(self.dp_switch_led)
        result["quickop_dp_switch_led"] = from_str(self.quickop_dp_switch_led)
        result["dp_switch_led_off"] = from_str(self.dp_switch_led_off)
        result["quickop_dp_bright_value_unit"] = from_str(self.quickop_dp_bright_value_unit)
        result["quickop_dp_switch_led_off"] = from_str(self.quickop_dp_switch_led_off)
        result["quickop_dp_bright_value"] = from_str(self.quickop_dp_bright_value)
        result["dp_switch_led_on"] = from_str(self.dp_switch_led_on)
        result["quickop_dp_switch_led_on"] = from_str(self.quickop_dp_switch_led_on)
        return result


class Shortcut:
    quick_op_dps: List[int]
    fault_dps: List[Any]
    display_dps: List[Any]
    switch_dp: int
    display_msgs: DisplayMsgs

    def __init__(self, quick_op_dps: List[int], fault_dps: List[Any], display_dps: List[Any], switch_dp: int, display_msgs: DisplayMsgs) -> None:
        self.quick_op_dps = quick_op_dps
        self.fault_dps = fault_dps
        self.display_dps = display_dps
        self.switch_dp = switch_dp
        self.display_msgs = display_msgs

    @staticmethod
    def from_dict(obj: Any) -> 'Shortcut':
        assert isinstance(obj, dict)
        quick_op_dps = from_list(from_int, obj.get("quickOpDps"))
        fault_dps = from_list(lambda x: x, obj.get("faultDps"))
        display_dps = from_list(lambda x: x, obj.get("displayDps"))
        switch_dp = from_int(obj.get("switchDp"))
        display_msgs = DisplayMsgs.from_dict(obj.get("displayMsgs"))
        return Shortcut(quick_op_dps, fault_dps, display_dps, switch_dp, display_msgs)

    def to_dict(self) -> dict:
        result: dict = {}
        result["quickOpDps"] = from_list(from_int, self.quick_op_dps)
        result["faultDps"] = from_list(lambda x: x, self.fault_dps)
        result["displayDps"] = from_list(lambda x: x, self.display_dps)
        result["switchDp"] = from_int(self.switch_dp)
        result["displayMsgs"] = to_class(DisplayMsgs, self.display_msgs)
        return result


class UIInfo:
    phase: str
    rn_find: bool
    app_rn_version: str
    ui: str
    type: str

    def __init__(self, phase: str, rn_find: bool, app_rn_version: str, ui: str, type: str) -> None:
        self.phase = phase
        self.rn_find = rn_find
        self.app_rn_version = app_rn_version
        self.ui = ui
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> 'UIInfo':
        assert isinstance(obj, dict)
        phase = from_str(obj.get("phase"))
        rn_find = from_bool(obj.get("rnFind"))
        app_rn_version = from_str(obj.get("appRnVersion"))
        ui = from_str(obj.get("ui"))
        type = from_str(obj.get("type"))
        return UIInfo(phase, rn_find, app_rn_version, ui, type)

    def to_dict(self) -> dict:
        result: dict = {}
        result["phase"] = from_str(self.phase)
        result["rnFind"] = from_bool(self.rn_find)
        result["appRnVersion"] = from_str(self.app_rn_version)
        result["ui"] = from_str(self.ui)
        result["type"] = from_str(self.type)
        return result


class MetaSchema:
    schema_info: SchemaInfo
    capability: int
    shortcut: Shortcut
    panel_config: PanelConfig
    ui_info: UIInfo
    i18_n_time: int
    attribute: int
    id: str
    category: str
    mesh_category: str
    support_group: bool

    def __init__(self, schema_info: SchemaInfo, capability: int, shortcut: Shortcut, panel_config: PanelConfig, ui_info: UIInfo, i18_n_time: int, attribute: int, id: str, category: str, mesh_category: str, support_group: bool) -> None:
        self.schema_info = schema_info
        self.capability = capability
        self.shortcut = shortcut
        self.panel_config = panel_config
        self.ui_info = ui_info
        self.i18_n_time = i18_n_time
        self.attribute = attribute
        self.id = id
        self.category = category
        self.mesh_category = mesh_category
        self.support_group = support_group

    @staticmethod
    def from_dict(obj: Any) -> 'MetaSchema':
        assert isinstance(obj, dict)
        schema_info = SchemaInfo.from_dict(obj.get("schemaInfo"))
        capability = from_int(obj.get("capability"))
        shortcut = Shortcut.from_dict(obj.get("shortcut"))
        panel_config = PanelConfig.from_dict(obj.get("panelConfig"))
        ui_info = UIInfo.from_dict(obj.get("uiInfo"))
        i18_n_time = from_int(obj.get("i18nTime"))
        attribute = from_int(obj.get("attribute"))
        id = from_str(obj.get("id"))
        category = from_str(obj.get("category"))
        mesh_category = from_str(obj.get("meshCategory"))
        support_group = from_bool(obj.get("supportGroup"))
        return MetaSchema(schema_info, capability, shortcut, panel_config, ui_info, i18_n_time, attribute, id, category, mesh_category, support_group)

    def to_dict(self) -> dict:
        result: dict = {}
        result["schemaInfo"] = to_class(SchemaInfo, self.schema_info)
        result["capability"] = from_int(self.capability)
        result["shortcut"] = to_class(Shortcut, self.shortcut)
        result["panelConfig"] = to_class(PanelConfig, self.panel_config)
        result["uiInfo"] = to_class(UIInfo, self.ui_info)
        result["i18nTime"] = from_int(self.i18_n_time)
        result["attribute"] = from_int(self.attribute)
        result["id"] = from_str(self.id)
        result["category"] = from_str(self.category)
        result["meshCategory"] = from_str(self.mesh_category)
        result["supportGroup"] = from_bool(self.support_group)
        return result


def meta_schema_from_dict(s: Any) -> List[MetaSchema]:
    return from_list(MetaSchema.from_dict, s)


def meta_schema_to_dict(x: List[MetaSchema]) -> Any:
    return from_list(lambda x: to_class(MetaSchema, x), x)
