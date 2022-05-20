import json
import numpy as np

from typing import Any, Dict, List


def convert_np_type_to_python(val):
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, np.integer):
        return int(val)
    if isinstance(val, np.floating):
        return float(val)
    return val


def convert_np_type(array):
    if isinstance(array, (np.ndarray, list)):
        return [convert_np_type_to_python(val) for val in array]
    return convert_np_type_to_python(array)


class GEMBase:

    def __init__(self):
        self._fields = {'type': 'base'}

    def render(self) -> dict:
        out = {}
        for k, v in self._fields.items():
            out[k] = convert_np_type(v)
        return out

    def to_json(self):
        return json.dumps(self.render())


class GEMContainer(GEMBase):
    def __init__(self, display_name: str = '', contents: List[GEMBase] = ()):
        super().__init__()

        self._fields = {'type': 'container'}  # type: Dict[str, Any]

        if display_name:
            self._fields['display-name'] = display_name

        self._contents = []
        self.set_contents(contents)

    def set_contents(self, contents: List[GEMBase]):
        for x in contents:
            if not isinstance(x, GEMBase):
                raise ValueError(f'GEM_Container passed non-GEM child {x}.')

        self._contents = contents

    def render(self) -> dict:
        self._fields['contents'] = [child.render() for child in self._contents]

        att_list = [x['attribution'] for x in self._fields['contents']]
        self._fields['attribution'] = sum(att_list)

        return super().render()


class GEMSimple(GEMBase):
    def __init__(
        self,
        display_name=None,
        feature_name=None,
        value=None,
        attribution=None,
        attribution_uncertainty=None,
    ):

        super().__init__()

        self._fields = {'type': 'simple'}

        if display_name is None and feature_name is None:
            raise ValueError(
                'GEM Simple fields must have "display_name", '
                '"feature_name", or both.'
            )

        if display_name is not None:
            self._fields['display-name'] = display_name

        if feature_name is not None:
            self._fields['feature-name'] = feature_name

        if value is not None:
            self._fields['value'] = value

        if attribution is not None:
            self._fields['attribution'] = attribution

        if attribution_uncertainty is not None:
            self._fields['attribution-uncertainty'] = attribution_uncertainty

    def set_attribution_uncertainty(self, attribution_uncertainty):
        self._fields['attribution-uncertainty'] = attribution_uncertainty


class GEMText(GEMBase):
    def __init__(
        self,
        display_name=None,
        feature_name=None,
        text_segments=None,
        text_attributions=None,
    ):
        super().__init__()

        self._fields = {'type': 'text'}

        if display_name is None and feature_name is None:
            raise ValueError(
                'GEM Simple fields must have "display_name", '
                '"feature_name", or both.'
            )

        if display_name:
            self._fields['display-name'] = display_name

        if feature_name:
            self._fields['feature-name'] = feature_name

        if text_segments is not None and text_attributions is not None:
            self.set_contents(text_segments, text_attributions)

    def set_contents(self, text_segments, text_attributions):
        if len(text_segments) != len(text_attributions):
            raise ValueError(
                'GEM_Text requires that "text_segments" and '
                '"text_attributions" must be lists of the same'
                f' length.  They were {len(text_segments)} '
                f'and {len(text_attributions)} respectively.'
            )

        self._fields['text-segments'] = text_segments
        self._fields['text-attributions'] = text_attributions

    def render(self):
        self._fields['attribution'] = sum(self._fields['text-attributions'])
        return super().render()
